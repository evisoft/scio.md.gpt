# Verification record — updated 2026-10-09

This report covers Scio 0.3.0, adapted from the existing Claude package. The owner reports a successful ChatGPT MCP connection. That run was not captured here. The ZIP is locally checked, not evidence of live write/review success or OpenAI approval. Pass sections are chronological; earlier hashes and test counts are historical. The summary table below records the current local result.

## Refresh — 2026-10-09

- Rechecked the current official OpenAI package, authentication, guidelines, testing and submission pages. The current submission guide permits importing `review.test_cases`, `review.demo_recording_url` and `publication.release_notes` from `plugin.json`; five positive and three negative cases and a reachable walkthrough remain required for first MCP review. Draft placeholders in `REVIEW.md` were not imported as if tested.
- Inspected the sibling platform at `2caf71d` in read-only mode. `/connect` still has the OAuth endpoint and hides `scio_register`; its 21 tool methods declare side-effect hints. No code adding per-tool `securitySchemes` was found in the MCP listing path, so the live wire response still needs inspection and likely a server change. This package cannot repair that server metadata.
- `python3 scripts/build.py` and 12 local unit/contract/package tests passed. The skill validator reported “Skill is valid!”; the 19-file ZIP passed `python3 -m zipfile -t` with SHA-256 `79c5d4efc9d39ae2d37ea6662c0ab6911892d24add9fd9c29cca17bcdcbd3afb`. Builder tests now reject an OAuth secret in an allowlisted file; the remote checker now compares live tool schemas, annotations and OAuth scope to the canonical contract when given a token. A concise release note is included in package metadata for portal import.
- `python3 scripts/check_remote.py` stopped at DNS resolution (`Temporary failure in name resolution`). No live OAuth, anonymous MCP, authenticated search, article read, assigned review, proposal, or ChatGPT desktop/mobile behavior was verified in this refresh. The public website, privacy notice, terms and support issue page were reachable through the web research tool; this does not prove MCP reachability.

## Continuation — 2026-10-09

- The remote checker now also validates authorization-server discovery, expected endpoint URLs, authorization-code flow, PKCE S256 and the `scio` scope before any authenticated calls. Its new regression test passes; 13 local tests now pass in total. The live attempt still ends at DNS before HTTP, so this is a stronger pending gate, not a live pass.
- A read-only comparison of the current platform source found 22 MCP tool attributes for 22 canonical tools and no differences in their `ReadOnly`, `Destructive` and `OpenWorld` values. This establishes source/contract consistency, not what the hosted `/connect` currently advertises.
- The computer-use environment exposed no browser surface; its in-app browser was unavailable. No portal, desktop or mobile test was therefore run.
- The icon's accessibility label now names Scio without asserting a fixed panel size; Scio's published rules vary panel size with community growth. The rebuilt 19-file ZIP passed the same local checks with SHA-256 `7a3ed6a3ccc0a17e1b71649e31bb3821c19466c17b51892086cb9e48ce7656d8`.
- The current submission error reference exposed a real manifest rejection: `Research` is not an accepted category. It is now `Education & Research`, with a regression check against the documented category list. The rebuilt ZIP passes 13 tests, skill validation and ZIP integrity; its latest SHA-256 is `ffd51847029d7b15760a1badb184ae557728f5910e54d89019ec66cd3055c23f`.
- The [21-tool annotation audit](docs/TOOL_ANNOTATIONS.md) records current source values. Several irreversible server actions still advertise `destructiveHint: false`; the platform owner must decide and correct those metadata values before the portal tool scan. OpenAI's current remote MCP review page also requires a global data residency project, verified publisher identity and `api.apps.write` permission.

## Listing and privacy pass — 2026-10-09

- Expanded local listing checks to the final-submission rules for package name, semantic version, supported category, text limits, normalized starter-prompt uniqueness, HTTPS URLs without embedded credentials, capability labels, icon size and light-theme brand contrast. All 13 tests still pass. These checks do not replace the OpenAI portal validator.
- Added an explicit skill boundary keeping payment card details, government identifiers, identifiable people's protected health information and authentication secrets out of Scio tool inputs. The public Scio privacy notice still needs an owner review of connector recipients and OAuth user controls against OpenAI's published privacy-policy rule.
- Rebuilt and checked the 19-file archive after the skill change. Current SHA-256: `84ec5698549a2dbe57b476b6801e70066af86a5518f130fa79a40acb82b43ec9`. No live MCP or ChatGPT test was performed in this pass.

## Tool-result and panel-access pass — 2026-10-09

- The authenticated MCP checker now rejects missing tool titles, missing canonical top-level result fields in `outputSchema`, duplicate tools or pagination cursors, and a foreign-panel read that returns panel material. `SCIO_TEST_FOREIGN_PANEL_ID` activates the last check with a dedicated test identity. This is a live check prepared for execution, not evidence of server authorization.
- `python3 -m unittest discover -s tests -v` passed 16 tests; `quick_validate.py skills/scio` reported “Skill is valid!”. `python3 scripts/check_remote.py` again failed at DNS resolution before any HTTP response. No live metadata, foreign-panel, ChatGPT or portal result was obtained.

## Reviewer and disclosure pass — 2026-10-09

- Rechecked the official [submission requirements](https://developers.openai.com/plugins/deploy/submission) and [tool guidance](https://developers.openai.com/plugins/plugin-guidelines). Five positive and three negative cases and a reviewer-accessible recording remain required for initial MCP review; the current draft cases are not represented as executed evidence.
- Corrected the reviewer fixture plan to require a dedicated test identity separate from developer and production operator identities. The gap-reservation case now asks for authorization of the exact temporary hold. The packaged skill clarifies that it uses Scio's served rules without verifying a cryptographic signature.
- The live [Scio terms](https://scio.md/terms) currently state that there is no human reading interface, while the proposed ChatGPT plugin displays Scio content to a human. This legal/product wording needs owner review on the hosted platform before submission.
- Rebuilt the 19-file archive after the skill correction. All 16 local tests, skill validation and ZIP integrity pass. Latest SHA-256: `914add19475cedb7bfc169ad107c1302c10df8932cfbc8b8300f0b2197a21811`.

## Listing copy and demo-access pass — 2026-10-09

- Replaced the manifest's promotional “superintelligence” description with concrete search, evidence, proposal and assigned-review capabilities, consistent with the current [OpenAI listing rule](https://developers.openai.com/plugins/plugin-guidelines#plugin-name-description-and-prompts). The package test now checks those factual claims instead of the removed slogan.
- The [OpenAI authenticated-MCP testing rule](https://developers.openai.com/plugins/plugin-guidelines#testing) requires a fully featured demo account with login and password and rejects inaccessible additional sign-in steps. The reviewer plan and owner checklist now call out Scio's Google sign-in and require a dedicated, accessible test account. This access has not been created or demonstrated.
- Rebuilt the 19-file ZIP. All 16 tests, skill validation and ZIP integrity pass. Latest SHA-256: `e00e38cfaecfdfc22d5f61bff9967d1fb9544d31fc321ccf0f0bf52f4e5bc55f`.
- The builder now also rejects raw JWT-shaped and Google OAuth access tokens in allowlisted files. A regression first showed the JWT gap, then passed after the scanner change. All 17 local tests, skill validation and ZIP integrity pass; the archive bytes and SHA-256 remain the same.

## Isolated Codex install — 2026-10-09

- Unpacked the current ZIP into a temporary local marketplace under `/tmp/scio-plugin-smoke-20261009`, with `CODEX_HOME` isolated in that same temporary tree. `codex plugin marketplace add` accepted the marketplace; `codex plugin add scio@scio-smoke --json` installed Scio version `0.3.0`; `codex plugin list --json` reported it enabled. This did not use a Scio or OpenAI user account.
- Compared every file in the Codex installed cache with its ZIP member: all 19 are present and byte-identical. This validates local package discovery and installation, not the remote MCP handshake, OAuth login, tool behavior, ChatGPT desktop/mobile or portal acceptance.
- In the same isolated profile, `codex mcp list --json` discovered an enabled `scio` Streamable HTTP entry at `https://scio.md/connect` with `auth_status: unknown`. This confirms the local MCP mapping is recognized; no authentication or network call succeeded.
- The current [Agent Plugins schemas](https://agent-plugins.org/schemas/1.0.0/plugin.schema.json) were rechecked. The package test now enforces the schema's lowercase plugin-name pattern and 64-character limit rather than accepting underscores or capitals.

## Time-bound reviewer fixture audit — 2026-10-09

- `python3 scripts/check_remote.py` still stopped at DNS resolution before HTTP. The computer-use environment still exposed no browser, so no current OAuth or ChatGPT case could be run.
- P4 now requires explanation and authorization before a possibly charged article read and before the edit submission. P3 now records the seat's `expires_at` and requires a fresh legitimate assignment for the reviewer test window; a spent or expired seat cannot be reused. The exact reviewer-access path remains unresolved on the platform and is a submission gate, not a passed local test.
- The opt-in remote checker now requires `SCIO_TEST_PANEL_ID` to appear in the connected agent's live `scio_whoami.assignments`. Immediately before an opt-in verdict it refreshes identity and requires at least two minutes until `expires_at`. The new boundary test passes; 18 local tests pass in total. No live seat was available to exercise this check here.

## MCP lifecycle correction — 2026-10-09

- The smoke client omitted `notifications/initialized` after `initialize`. The [MCP 2025-06-18 lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle) requires that notification before normal operations, and [Streamable HTTP](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports) requires HTTP 202 with no body for an accepted notification. The checker now validates the negotiated version, sends the notification without an `id`, and checks the HTTP response. A failing regression was added first; all 19 local tests now pass.
- The server source uses a stateless HTTP transport, so the checker does not need to persist an MCP session ID. The corrected lifecycle still needs a live run; DNS resolution blocks it in this environment.

## Skill import metadata audit — 2026-10-09

- The current [OpenAI submission error reference](https://developers.openai.com/plugins/deploy/submission-errors) requires `interface.display_name` and `interface.short_description` when `agents/openai.yaml` is present. This package previously omitted `interface`; a new test reproduced the resulting gap. The YAML now declares both fields while retaining the MCP dependency, and the unused `SKILL.md` metadata block was removed.
- The packaged skill has 15 files, about 109 KiB uncompressed and 48 KiB compressed, well below a MiB. The exact portal-reported compressed limit has not been observed; local size is not a portal import result.
- Rebuilt the 19-file ZIP. All 19 local tests, skill validation and archive integrity pass; SHA-256: `b74a547f996081d7af2f247d3711e963ad082be1699700b27dd207674d5b8372`.
- Reinstalled this final ZIP through a fresh, isolated Codex marketplace under `/tmp/scio-plugin-smoke-20261009-final`. `codex plugin add` accepted `scio` 0.3.0, `codex mcp list --json` discovered an enabled Streamable HTTP mapping to `https://scio.md/connect`, and all 19 installed files matched the ZIP byte-for-byte. Codex reported `auth_status: unknown`; no live OAuth or tool call was made.

| Gate | Evidence | Status |
|---|---|---|
| Source comparison | Inspected Claude plugin `../scio.md.claude` at `cd021b9` and canonical server `../scio` at `2caf71d`. `/connect` source hides/refuses `scio_register` and maps 21 other tools; platform contract has 22 total. | Source confirmed, wire pending |
| Claude source baseline | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` in `../scio.md.claude`: 20 passed. These are the sibling package's checks, not OpenAI approval. | Passed read-only |
| Claude adaptation | Bundled portable research, writing, review, translation, maintenance, security, Markdown, style, actions, connection, team, rules and claim-schema references. No Claude command, agent definition or local runtime is in the ZIP. | Checked locally |
| Package and checker tests | `python3 -m unittest discover -s tests -v`: 19 passed, including listing shape, relative links, tool names, connector exclusion, paged review schema, claim fields, ZIP bytes, secret and symlink rejection, MCP lifecycle, SSE parsing and redirect refusal. | Passed locally |
| Skill format and script syntax | `quick_validate.py skills/scio`: “Skill is valid!”; `python3 -m py_compile` passed for all build/check/test Python files. | Passed locally |
| ZIP | `python3 scripts/build.py`; 19 allowlisted files including `LICENSE`, 55,552 bytes; `python3 -m zipfile -t` passed. SHA-256: `b74a547f996081d7af2f247d3711e963ad082be1699700b27dd207674d5b8372`. Fresh isolated Codex install copied all 19 files identically and discovered `/connect`. | Passed locally |
| Live OAuth discovery | `python3 scripts/check_remote.py` failed before HTTP with temporary DNS resolution failure in this workspace. A previous review observed protected-resource metadata, but it was not refreshed here. The script now refuses HTTP redirects before sending a bearer token. | Not verified here |
| Authenticated tool scan and calls | No OAuth test token or dedicated identity was available here. No live `tools/list`, source/article read, proposal, assigned seat or verdict was captured. The script has opt-in calls for dedicated tests. | Not run here |
| ChatGPT/Codex behavior, review and portal | Five positive and three negative cases are drafts. No recorded desktop/mobile runs, demo URL, OpenAI tool scan, domain challenge, upload, approval or publication. | Pending |

## Remaining verification

Current workspace check on 2026-10-09: `scripts/check_remote.py` still fails at DNS resolution before HTTP, `SCIO_OAUTH_ACCESS_TOKEN` is absent, and the computer-use surface exposes no browser. The local 19-test suite passes. Live OAuth, ChatGPT desktop/mobile and portal review cannot be certified from this workspace until external access and a dedicated reviewer identity are available.

1. Run the [server checks](SERVER_CHANGES.md) with a dedicated identity: OAuth discovery, all 21 connector tools, security schemes, annotations, scopes, rank and panel authorization. Verify `scio_register` is absent and directly refused, while legacy `/mcp` still works.
2. Run the [review cases](REVIEW.md) in ChatGPT developer mode and Codex where available. Use safe sample articles, a genuine assigned review seat and point/quota balance. Confirm every panel page is read before review. Record exact tool calls and visible answers; make a redacted reviewer-accessible recording.
3. Resolve the [OpenAI requirements audit](docs/OPENAI_REQUIREMENTS.md), recheck current listing URLs and privacy disclosures, rebuild after any packaged change, then perform owner-authorized portal steps. Credentials must go through the portal privately, not into the ZIP.
