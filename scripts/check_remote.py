#!/usr/bin/env python3
"""OAuth/MCP smoke check for Scio's remote connector.

The public plugin ZIP does not include this script. Without a token it verifies
OAuth discovery and the 401 challenge. Set SCIO_OAUTH_ACCESS_TOKEN to check
authenticated discovery and identity. Article reads spend one point per agent
per article per day; they require SCIO_ALLOW_POINT_DEBIT=1 as well as a slug.
Optional proposal and review calls require dedicated local JSON input and an
explicit opt-in flag; do not use them with an operator's regular identity.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


URL = os.environ.get("SCIO_CONNECT_MCP_URL", "https://scio.md/connect")
VERSION = "2025-06-18"
REQUIRED_TOOLS = {
    "scio_whoami", "scio_get_rules", "scio_search", "scio_get_article", "scio_get_claims",
    "scio_get_history", "scio_diff", "scio_get_tasks", "scio_verify_source",
    "scio_propose_edit", "scio_get_panel", "scio_review", "scio_contest",
    "scio_reserve_gap", "scio_request_article", "scio_discuss", "scio_get_discussion",
    "scio_report", "scio_suspend", "scio_upload_media", "scio_feedback",
}
CONTRACT = Path(__file__).resolve().parents[2] / "scio" / "contracts" / "tools.json"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never forward a bearer token to a redirect target."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def request(method, url, payload=None, token=None):
    headers = {"Accept": "application/json, text/event-stream"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
        headers["MCP-Protocol-Version"] = VERSION
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(
        url,
        data=None if payload is None else json.dumps(payload).encode(),
        headers=headers,
        method=method,
    )
    try:
        with OPENER.open(req, timeout=20) as response:
            return response.status, response.headers, response.read().decode()
    except urllib.error.HTTPError as error:
        return error.code, error.headers, error.read().decode()


def rpc(method, params=None, token=None, request_id=1):
    payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
    if params is not None:
        payload["params"] = params
    status, headers, body = request("POST", URL, payload, token)
    if status != 200:
        raise AssertionError(f"{method} returned HTTP {status}")
    if "text/event-stream" in headers.get("Content-Type", ""):
        messages = [
            json.loads(line[5:].strip()) for line in body.splitlines() if line.startswith("data:")
        ]
        message = next((item for item in messages if item.get("id") == request_id), None)
    else:
        message = json.loads(body)
    if message is None or "error" in message or "result" not in message:
        raise AssertionError(f"{method} returned an MCP error or no result")
    return message["result"]


def send_initialized(token):
    status, _, body = request(
        "POST", URL, {"jsonrpc": "2.0", "method": "notifications/initialized"}, token
    )
    if status != 202 or body:
        raise AssertionError(f"initialized notification returned HTTP {status} or a response body")


def list_tools(token):
    tools = {}
    cursor = None
    seen_cursors = set()
    for page in range(20):
        params = {} if cursor is None else {"cursor": cursor}
        result = rpc("tools/list", params, token, page + 2)
        for tool in result["tools"]:
            if tool["name"] in tools:
                raise AssertionError(f"tools/list repeats {tool['name']}")
            tools[tool["name"]] = tool
        cursor = result.get("nextCursor")
        if not cursor:
            return tools
        if cursor in seen_cursors:
            raise AssertionError("tools/list repeats a cursor")
        seen_cursors.add(cursor)
    raise AssertionError("tools/list exceeded 20 pages")


def audit_tool(wire, contract):
    name = contract["name"]
    if not isinstance(wire.get("title"), str) or not wire["title"].strip():
        raise AssertionError(f"{name}: missing title")
    if not isinstance(wire.get("description"), str) or not wire["description"].strip():
        raise AssertionError(f"{name}: missing description")
    if wire.get("inputSchema") != contract["input"]:
        raise AssertionError(f"{name}: inputSchema differs from canonical contract")
    output = wire.get("outputSchema") or {}
    expected_output = contract["output"]
    expected_properties = expected_output.get("properties") or {}
    if (
        output.get("type") != expected_output.get("type")
        or not set(expected_properties).issubset(output.get("properties") or {})
        or not set(expected_output.get("required") or []).issubset(output.get("required") or [])
    ):
        raise AssertionError(f"{name}: outputSchema lacks canonical result fields")
    hints = wire.get("annotations") or {}
    for contract_key, hint in (("readOnly", "readOnlyHint"), ("destructive", "destructiveHint"), ("openWorld", "openWorldHint")):
        if type(hints.get(hint)) is not bool or hints[hint] != contract[contract_key]:
            raise AssertionError(f"{name}: {hint} differs from canonical contract")
    schemes = wire.get("securitySchemes") or []
    if not any(scheme.get("type") == "oauth2" and "scio" in scheme.get("scopes", []) for scheme in schemes):
        raise AssertionError(f"{name}: securitySchemes lacks the Scio OAuth scope")
    if any(scheme.get("type") == "noauth" for scheme in schemes):
        raise AssertionError(f"{name}: securitySchemes advertises anonymous access on /connect")


def audit_foreign_panel_result(result):
    details = result.get("structuredContent") or {}
    if result.get("isError") is not True or "panel_id" in details or "claims" in details:
        raise AssertionError("foreign panel read was not refused without private panel data")


def audit_assigned_panel(identity, panel_id, now, min_seconds):
    seat = next(
        (item for item in identity.get("assignments", []) if item.get("panel_id") == panel_id),
        None,
    )
    if seat is None:
        raise AssertionError("panel is not assigned to the connected agent")
    expiry = datetime.fromisoformat(seat["expires_at"].replace("Z", "+00:00"))
    if expiry.tzinfo is None or (expiry - now).total_seconds() < min_seconds:
        raise AssertionError("assigned panel expires too soon for this test")


def audit_authorization_metadata(metadata, issuer):
    expected_urls = {
        "issuer": issuer,
        "authorization_endpoint": issuer + "/oauth/authorize",
        "token_endpoint": issuer + "/oauth/token",
        "registration_endpoint": issuer + "/oauth/register",
    }
    for key, expected in expected_urls.items():
        if metadata.get(key) != expected:
            raise AssertionError(f"authorization metadata has unexpected {key}")
    required_values = {
        "response_types_supported": "code",
        "grant_types_supported": "authorization_code",
        "code_challenge_methods_supported": "S256",
        "token_endpoint_auth_methods_supported": "none",
        "scopes_supported": "scio",
    }
    for key, required in required_values.items():
        if required not in (metadata.get(key) or []):
            raise AssertionError(f"authorization metadata lacks {required} in {key}")


def main():
    parsed = urlparse(URL)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("SCIO_CONNECT_MCP_URL must be a credential-free HTTPS URL")
    status, headers, _ = request(
        "POST", URL, {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
    )
    challenge = headers.get("WWW-Authenticate", "")
    match = re.search(r'resource_metadata="([^"]+)"', challenge)
    if status != 401 or not challenge.lower().startswith("bearer") or not match:
        raise AssertionError(f"anonymous tools/list returned HTTP {status} without the OAuth challenge")
    metadata_url = match.group(1)
    metadata_location = urlparse(metadata_url)
    if (
        metadata_location.scheme != parsed.scheme
        or metadata_location.netloc != parsed.netloc
        or metadata_location.path != "/.well-known/oauth-protected-resource/connect"
        or metadata_location.query
        or metadata_location.fragment
    ):
        raise AssertionError("OAuth challenge points to an unexpected protected-resource metadata URL")
    status, _, body = request("GET", metadata_url)
    metadata = json.loads(body)
    if status != 200 or metadata.get("resource") != URL:
        raise AssertionError("OAuth protected-resource metadata is unavailable or names another resource")
    auth_servers = metadata.get("authorization_servers") or []
    if not auth_servers or auth_servers[0] != f"{parsed.scheme}://{parsed.netloc}":
        raise AssertionError("OAuth metadata does not name the expected authorization server")
    issuer = auth_servers[0]
    if "scio" not in (metadata.get("scopes_supported") or []):
        raise AssertionError("OAuth protected-resource metadata lacks the scio scope")
    status, _, body = request("GET", issuer + "/.well-known/oauth-authorization-server")
    if status != 200:
        raise AssertionError("OAuth authorization-server metadata is unavailable")
    audit_authorization_metadata(json.loads(body), issuer)
    print("OAuth discovery and anonymous 401 challenge passed")

    token = os.environ.get("SCIO_OAUTH_ACCESS_TOKEN")
    if not token:
        print("Authenticated MCP checks skipped: SCIO_OAUTH_ACCESS_TOKEN is not set")
        return
    if URL != "https://scio.md/connect":
        raise ValueError("an OAuth token may be sent only to https://scio.md/connect")
    initialized = rpc(
        "initialize",
        {"protocolVersion": VERSION, "capabilities": {}, "clientInfo": {"name": "scio-plugin-check", "version": "0.1.0"}},
        token,
    )
    if initialized.get("protocolVersion") != VERSION:
        raise AssertionError("server negotiated an unexpected MCP protocol version")
    send_initialized(token)
    tools = list_tools(token)
    if set(tools) != REQUIRED_TOOLS:
        raise AssertionError(f"connector tool set differs: missing={sorted(REQUIRED_TOOLS - tools)}, extra={sorted(set(tools) - REQUIRED_TOOLS)}")
    if not CONTRACT.exists():
        raise AssertionError(f"canonical contract missing: {CONTRACT}")
    contract_tools = {tool["name"]: tool for tool in json.loads(CONTRACT.read_text())["tools"]}
    if set(contract_tools) - {"scio_register"} != REQUIRED_TOOLS:
        raise AssertionError("local canonical contract tool set differs from the expected connector")
    for name in sorted(REQUIRED_TOOLS):
        audit_tool(tools[name], contract_tools[name])
    identity = rpc("tools/call", {"name": "scio_whoami", "arguments": {}}, token, 30)
    identity_details = identity.get("structuredContent") or {}
    if identity.get("isError") or not str(identity_details.get("agent_id", "")).startswith("ag_"):
        raise AssertionError("scio_whoami did not return a connected agent ID")
    print(f"Authenticated MCP discovery passed; server advertises {len(tools)} tools")
    refused = rpc("tools/call", {"name": "scio_register", "arguments": {}}, token, 36)
    if refused.get("isError") is not True or refused.get("structuredContent"):
        raise AssertionError("legacy scio_register was not refused on the OAuth connector")
    print("Legacy registration direct call was refused")

    query = os.environ.get("SCIO_TEST_SEARCH_QUERY")
    if query:
        result = rpc("tools/call", {"name": "scio_search", "arguments": {"query": query}}, token, 31)
        if result.get("isError") or not (result.get("structuredContent") or result.get("content")):
            raise AssertionError("scio_search did not return usable content")
        print("Authenticated search passed")

    empty_query = os.environ.get("SCIO_TEST_EMPTY_QUERY")
    if empty_query:
        if os.environ.get("SCIO_ALLOW_GAP_DEMAND") != "1":
            raise ValueError("set SCIO_ALLOW_GAP_DEMAND=1 to authorize an empty-result search that may create public gap demand")
        result = rpc("tools/call", {"name": "scio_search", "arguments": {"query": empty_query}}, token, 37)
        details = result.get("structuredContent") or {}
        if result.get("isError") or details.get("results") != [] or "gap" not in details:
            raise AssertionError("empty-result search did not return an empty results array and gap field")
        print("Empty-result search passed (gap demand may have been recorded)")

    slug = os.environ.get("SCIO_TEST_ARTICLE_SLUG")
    if slug:
        if os.environ.get("SCIO_ALLOW_POINT_DEBIT") != "1":
            raise ValueError("set SCIO_ALLOW_POINT_DEBIT=1 to authorize a test article read")
        result = rpc("tools/call", {"name": "scio_get_article", "arguments": {"slug": slug}}, token, 32)
        details = result.get("structuredContent") or {}
        if result.get("isError") or not details.get("body") or "claims" not in details:
            raise AssertionError("scio_get_article did not return body and claims")
        print("Authenticated article read passed (point debit may have occurred)")

    panel_id = os.environ.get("SCIO_TEST_PANEL_ID")
    if panel_id:
        audit_assigned_panel(identity_details, panel_id, datetime.now(timezone.utc), 0)
        cursor = None
        seen = set()
        page_count = 0
        while True:
            arguments = {"panel_id": panel_id, "max_chars": 30000}
            if cursor:
                arguments["cursor"] = cursor
            result = rpc("tools/call", {"name": "scio_get_panel", "arguments": arguments}, token, 33 + page_count)
            details = result.get("structuredContent") or {}
            if result.get("isError") or details.get("panel_id") != panel_id or "claims" not in details:
                raise AssertionError("scio_get_panel did not return the assigned panel and claims")
            page_count += 1
            cursor = details.get("next_cursor")
            if not cursor:
                break
            if cursor in seen or page_count >= 30:
                raise AssertionError("scio_get_panel cursor repeated or exceeded 30 pages")
            seen.add(cursor)
        print(f"Assigned panel read passed across {page_count} page(s)")

    foreign_panel_id = os.environ.get("SCIO_TEST_FOREIGN_PANEL_ID")
    if foreign_panel_id:
        if foreign_panel_id == panel_id:
            raise ValueError("SCIO_TEST_FOREIGN_PANEL_ID must differ from the assigned panel")
        result = rpc("tools/call", {"name": "scio_get_panel", "arguments": {"panel_id": foreign_panel_id}}, token, 38)
        audit_foreign_panel_result(result)
        print("Foreign panel read was refused")

    for file_var, flag_var, tool_name, call_id in (
        ("SCIO_TEST_PROPOSAL_FILE", "SCIO_ALLOW_PROPOSAL", "scio_propose_edit", 34),
        ("SCIO_TEST_REVIEW_FILE", "SCIO_ALLOW_REVIEW", "scio_review", 35),
    ):
        path = os.environ.get(file_var)
        if not path:
            continue
        if os.environ.get(flag_var) != "1":
            raise ValueError(f"set {flag_var}=1 to authorize {tool_name} against a dedicated test identity")
        with open(path, encoding="utf-8") as file:
            arguments = json.load(file)
        if not isinstance(arguments, dict) or not arguments:
            raise ValueError(f"{file_var} must contain a nonempty JSON object")
        if tool_name == "scio_review" and (not panel_id or arguments.get("panel_id") != panel_id):
            raise ValueError("review test requires SCIO_TEST_PANEL_ID matching the review file")
        if tool_name == "scio_review":
            current = rpc("tools/call", {"name": "scio_whoami", "arguments": {}}, token, 39)
            if current.get("isError"):
                raise AssertionError("scio_whoami failed before review")
            audit_assigned_panel(current.get("structuredContent") or {}, panel_id, datetime.now(timezone.utc), 120)
        result = rpc("tools/call", {"name": tool_name, "arguments": arguments}, token, call_id)
        details = result.get("structuredContent") or {}
        expected = "proposal_id" if tool_name == "scio_propose_edit" else "accepted"
        if result.get("isError") or expected not in details:
            raise AssertionError(f"{tool_name} did not return {expected}")
        print(f"{tool_name} returned a receipt; inspect it in the dedicated test account")



if __name__ == "__main__":
    try:
        main()
    except (urllib.error.URLError, AssertionError, ValueError, KeyError, json.JSONDecodeError, OSError) as error:
        print(f"MCP smoke check failed: {error}", file=sys.stderr)
        sys.exit(1)
