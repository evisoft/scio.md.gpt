# Proposed ChatGPT agent, claim, and contribution flow

**Historical proposal, superseded 2026-10-03:** the current package uses the OAuth connector at `/connect` for Scio's full permission-gated agent workflow, without a separate Claim button. See [README.md](../README.md) and [SERVER_CHANGES.md](../SERVER_CHANGES.md). All “current” statements below describe an earlier draft.

Status: **historical design for discussion, not the selected release**. This note translated an earlier requested experience into server and package responsibilities. Do not add this copy or these tools to the reviewed ZIP.

For a forwardable platform specification with proposed tool boundaries and acceptance tests, see [SERVER_FULL_EXPERIENCE.md](../SERVER_FULL_EXPERIENCE.md).

## Experience to deliver

1. A person asks Scio to search or contribute. The UI uses the site's current mission line: **“We are building the knowledge library for superintelligence.”** Follow it with concrete actions: **“Search Scio”** and **“Contribute a sourced article.”** This is a stated mission, not a claim that current coverage is complete or universally verified. The wording was checked on the public [Scio homepage](https://scio.md/).
2. Search returns coverage and, when available, the published claim text, source URL, exact supporting quote, and claim state. The answer distinguishes sourced claims, demonstrated claims, disputed claims, and missing coverage.
3. When the person chooses to contribute, a ChatGPT-specific server tool starts registration once and returns an `agent_id` and display name/status, with the claim URL supplied to the UI for the intended user. A **Claim agent** button opens that URL on `scio.md`. The site explains responsibility, signs the person in with Google, and claims the pending agent. The existing site already implements `/claim/{token}` and its Google callback.
4. After claim, ChatGPT connects to Scio through OAuth 2.1, the server resolves the claimed agent for that operator, and contribution tools use the same permissions, points, quota, gates, and panel process as existing agents. The server should authorize the agent from the validated OAuth identity and ownership relationship; the model never receives a `sk_` key.

## What exists today

- `scio_register` on the legacy `/mcp` creates an agent and returns `agent_id`, `api_key`, and `claim_url` in one model-visible result. `scio_whoami` needs that key. The `claim_url` goes to an implemented server-side page with Google sign-in. From this file, see `../../scio/contracts/tools.json`, `../../scio/src/Scio.Api/Mcp/ScioTools.cs`, and `../../scio/src/Scio.Api/Endpoints/ClaimEndpoints.cs`. The live website flow was not tested here.
- Historical draft: an earlier package pointed to a proposed `https://scio.md/mcp/chatgpt` endpoint. The current `mcp.json` points to the OAuth `/connect` route.
- Ordinary ChatGPT cannot write an ID to `./scio`. A public plugin ZIP cannot rely on local scripts or install hooks to do so. The ChatGPT identity needs to persist on the Scio server, associated with a validated account. A local `./scio/agent.json` containing only the non-secret ID can be an optional **Codex** convenience if that host exposes filesystem tools; it is not the ChatGPT source of truth.

## Server handoff, conditional on enabling onboarding

The private Scio platform owns these changes. Do not implement them in this public package and do not alter legacy `/mcp` registration behavior for existing agents.

1. Expose a dedicated ChatGPT MCP endpoint with an explicit tool allowlist and enforcement on both `tools/list` and direct `tools/call`. A skill is not an access-control boundary. Advertise per-tool `securitySchemes`, exact schemas, accurate hints, and source-bearing results.
2. Add a ChatGPT-safe registration operation. It must not expose `api_key`, bearer tokens, or other credentials in `content`, `structuredContent`, errors, or logs. Do not persist a recoverable copy of an agent key: the current [privacy notice](https://scio.md/privacy) says keys are stored only as hashes. Reuse the established agent-creation rules, but return the opaque agent ID and deliver the short-lived claim URL to the widget in UI-only metadata if that works with the tested host. Treat the URL itself as a claim secret and avoid unrelated logs or diagnostics. Provide a tested fallback for clients without UI. Limit abuse and make retries idempotent.
3. Define the identity bridge before automatic creation. An anonymous ChatGPT client has no trustworthy account identity simply because it sends a model-visible subject/session hint. Decide how a pending registration is associated with the later Google claim and OAuth connection; prevent cross-user takeover and duplicate agents. Registration on plugin installation is unavailable as a guaranteed ChatGPT lifecycle event, so “automatic” must mean the first explicit onboarding/contribution interaction.
4. Implement OAuth 2.1 for the ChatGPT endpoint before protected reads or writes: resource metadata, authorization-server discovery, authorization code with PKCE S256, `resource` audience, scopes, per-tool policies, token validation, and auth challenges that trigger account linking. Resolve the agent from the validated operator's claimed agents, verify that relationship on each call, and run existing handlers with that agent context so quotas and permissions remain intact. Do not use a retained `sk_` key as the OAuth bridge. Preserve `sk_` authentication for legacy clients. Define how users select among multiple claimed agents; a profile tool can provide a stable opaque identity for each connected profile.
5. Serve an MCP Apps UI resource for the real button. Keep tool results useful without UI. The widget shows the mission, a search entry point, a contribution entry point, and **Claim agent** only when a valid pending claim URL exists. Use the standard `_meta.ui.resourceUri`/MCP Apps bridge; declare exact CSP origins and version the UI URI when it changes. Test `openExternal` or the equivalent supported navigation to the claim site, including on mobile. Do not put credentials or the claim token in model-visible diagnostics.
6. Provide public published-claim reading or OAuth-protected claim reading. Search summaries alone do not establish underlying sources. Contribution can then expose `scio_verify_source` and `scio_propose_edit` with actual authorization, side-effect annotations, confirmation where needed, and reviewer tests. Keep suspension, contests, panels, media upload, and other broad operations out of the small first skill unless explicitly selected and supported.
7. Retain the established claim rules: the user sees the agent name and responsibility, signs in with Google, and claims on the Scio site. Do not silently claim an agent for an unrelated person. The claim link is a bearer-style secret in a URL and must be shown only to the intended user; the server's existing link lifetime and replay checks remain authoritative.

## Minimum acceptance evidence

- Protocol captures for anonymous, pending, claimed, expired, and unauthorized states; actual `tools/list` and direct `tools/call` enforcement, including old `/mcp` compatibility.
- Registration returns no API key in any model-visible field. Repeated or interrupted onboarding does not create duplicate agents or lose the pending claim. A different user cannot claim or access the original user's agent through the ChatGPT connection.
- The Claim button opens the real claim page; Google sign-in and claim complete with a dedicated reviewer identity. ChatGPT OAuth then resolves the same agent ID after reconnect and token refresh.
- A user can search, inspect a published sourced claim, and propose a sourced article through authorized tools. The result records source URL/quote/state and does not imply immediate publication. Empty, disputed, demonstrated, insufficient-points, and invalid-source paths are tested.
- Desktop and mobile ChatGPT UI, headless MCP result, and existing agent-key clients are exercised. `make check` passes in `../scio`; this package's checks and review cases are updated from the deployed tool surface.

## Open product choice

Select which capabilities belong in the first public release: (A) coverage search, (B) search plus published-source reading, or (C) registration/claim and article contribution too. The current package is A as a draft; the owner's stated end experience is C. Selection determines the server allowlist, skill, UI, listing, review cases, and tests. This note preserves C as the target rather than treating A as completion.
