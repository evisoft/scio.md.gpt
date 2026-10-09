"""Local protocol and credential-safety checks for the opt-in smoke script."""

import importlib.util
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_remote.py"
SPEC = importlib.util.spec_from_file_location("check_remote", SCRIPT)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class RemoteCheckerTests(unittest.TestCase):
    @staticmethod
    def wire_tool(source):
        return {
            "name": source["name"], "title": "Readable tool title",
            "description": "A useful tool description.",
            "inputSchema": source["input"],
            "outputSchema": source["output"],
            "annotations": {
                "readOnlyHint": source["readOnly"],
                "destructiveHint": source["destructive"],
                "openWorldHint": source["openWorld"],
            },
            "securitySchemes": [{"type": "oauth2", "scopes": ["scio"]}],
        }

    def test_redirect_is_never_followed(self):
        self.assertIsNone(checker.NoRedirect().redirect_request(
            None, None, 302, "Found", {}, "https://other.example/collect"
        ))

    def test_sse_accepts_data_without_optional_space(self):
        body = 'event: message\ndata:{"jsonrpc":"2.0","id":7,"result":{"tools":[]}}\n\n'
        with patch.object(checker, "request", return_value=(200, {"Content-Type": "text/event-stream"}, body)):
            self.assertEqual(checker.rpc("tools/list", {}, "test-token", 7), {"tools": []})

    def test_mcp_error_is_not_treated_as_success(self):
        body = '{"jsonrpc":"2.0","id":7,"error":{"code":-32601,"message":"Unknown tool"}}'
        with patch.object(checker, "request", return_value=(200, {"Content-Type": "application/json"}, body)):
            with self.assertRaises(AssertionError):
                checker.rpc("tools/list", {}, "test-token", 7)

    def test_initialized_notification_has_no_id_and_requires_202(self):
        with patch.object(checker, "request", return_value=(202, {}, "")) as send:
            checker.send_initialized("test-token")
        self.assertEqual(send.call_args.args, (
            "POST", checker.URL, {"jsonrpc": "2.0", "method": "notifications/initialized"}, "test-token"
        ))
        with patch.object(checker, "request", return_value=(200, {}, "{}")):
            with self.assertRaisesRegex(AssertionError, "initialized notification"):
                checker.send_initialized("test-token")

    def test_metadata_audit_rejects_wrong_side_effect_annotation(self):
        contract = json.loads((SCRIPT.parents[2] / "scio" / "contracts" / "tools.json").read_text())
        source = next(tool for tool in contract["tools"] if tool["name"] == "scio_get_article")
        wire = self.wire_tool(source)
        wire["annotations"]["readOnlyHint"] = True
        with self.assertRaisesRegex(AssertionError, "readOnlyHint"):
            checker.audit_tool(wire, source)

    def test_metadata_audit_rejects_missing_oauth_scope(self):
        contract = json.loads((SCRIPT.parents[2] / "scio" / "contracts" / "tools.json").read_text())
        source = next(tool for tool in contract["tools"] if tool["name"] == "scio_get_claims")
        wire = self.wire_tool(source)
        wire["securitySchemes"][0]["scopes"] = []
        with self.assertRaisesRegex(AssertionError, "securitySchemes"):
            checker.audit_tool(wire, source)

    def test_metadata_audit_rejects_missing_title(self):
        contract = json.loads((SCRIPT.parents[2] / "scio" / "contracts" / "tools.json").read_text())
        source = next(tool for tool in contract["tools"] if tool["name"] == "scio_search")
        wire = self.wire_tool(source)
        wire["title"] = ""
        with self.assertRaisesRegex(AssertionError, "title"):
            checker.audit_tool(wire, source)

    def test_metadata_audit_rejects_missing_output_field(self):
        contract = json.loads((SCRIPT.parents[2] / "scio" / "contracts" / "tools.json").read_text())
        source = next(tool for tool in contract["tools"] if tool["name"] == "scio_search")
        wire = self.wire_tool(source)
        wire["outputSchema"] = {"type": "object", "properties": {"results": {}}, "required": ["results"]}
        with self.assertRaisesRegex(AssertionError, "outputSchema"):
            checker.audit_tool(wire, source)

    def test_foreign_panel_refusal_rejects_returned_private_data(self):
        with self.assertRaisesRegex(AssertionError, "foreign panel"):
            checker.audit_foreign_panel_result({"isError": False, "structuredContent": {"panel_id": "panel-other"}})

    def test_assigned_panel_requires_time_for_verdict(self):
        now = datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)
        identity = {"assignments": [{"panel_id": "pn_assigned", "expires_at": "2026-10-09T12:01:00Z"}]}
        with self.assertRaisesRegex(AssertionError, "expires too soon"):
            checker.audit_assigned_panel(identity, "pn_assigned", now, 120)
        with self.assertRaisesRegex(AssertionError, "not assigned"):
            checker.audit_assigned_panel(identity, "pn_other", now, 0)

    def test_authorization_metadata_requires_pkce_s256(self):
        metadata = {
            "issuer": "https://scio.md",
            "authorization_endpoint": "https://scio.md/oauth/authorize",
            "token_endpoint": "https://scio.md/oauth/token",
            "registration_endpoint": "https://scio.md/oauth/register",
            "response_types_supported": ["code"],
            "grant_types_supported": ["authorization_code", "refresh_token"],
            "code_challenge_methods_supported": ["plain"],
            "token_endpoint_auth_methods_supported": ["none"],
            "scopes_supported": ["scio"],
        }
        with self.assertRaisesRegex(AssertionError, "S256"):
            checker.audit_authorization_metadata(metadata, "https://scio.md")


if __name__ == "__main__":
    unittest.main()
