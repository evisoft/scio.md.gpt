# Scio server handoff: proposed ChatGPT experience

**Historical proposal, superseded 2026-10-03:** the current package uses the OAuth connector at `/connect` for the full permission-gated agent workflow, without separate Claim tooling. Use [SERVER_CHANGES.md](SERVER_CHANGES.md) for current platform work. All “current” statements below describe the earlier design context.

**Status:** specification for the Scio platform team, not implemented, deployed, or selected for the first public release. The owner will choose the first-release tool set. This document covers the requested end experience if onboarding and contribution are selected. No .NET implementation belongs in this public plugin repository.

## Existing contracts to preserve

- The canonical contract is `../scio/contracts/tools.json`; the live implementation is `../scio/src/Scio.Api/Mcp/ScioTools.cs`. The current `/mcp` has 22 tools and existing `sk_` clients. Keep that endpoint and those clients working.
- Legacy `scio_register` returns `agent_id`, `api_key`, and `claim_url` together. It is unsuitable as the ChatGPT registration tool because the key would enter model-visible output. Existing keys are stored only as hashes according to the [Scio privacy notice](https://scio.md/privacy); do not add recoverable key storage for this integration.
- `scio_search` works anonymously but returns coverage summaries, not underlying citations. `scio_get_claims` returns claim text, source, quote, and state, but currently requires a key. `scio_verify_source` and `scio_propose_edit` also require a key. Article proposals enter gates and review; they are not instantly published.
- `/claim/{token}` already presents the agent and responsibility, starts Google sign-in, and claims the agent through its callback. Keep its established rules and token checks.

## Proposed endpoint and tool surface

Expose `https://scio.md/mcp/chatgpt` as an HTTPS Streamable HTTP MCP endpoint. Enforce an explicit allowlist during `tools/list` **and** direct `tools/call`; do not rely on the skill to hide tools. Check resources, prompts, server instructions, schemas, security metadata, and errors as well. The following names are proposals, not additions to the canonical contract yet:

| Proposed tool | Access | Result and boundary |
|---|---|---|
| `scio_search` | Anonymous | Reuse existing search. Return title, state, summary, and stable slug; describe these as coverage discovery. |
| `scio_get_public_claims` | Anonymous, if the platform permits public published claims | Given slug and optional language/cursor, return only currently published claim text, support state, source URL and exact quote when present, plus stable claim/revision IDs. Exclude pending/private revisions. If the platform instead requires an account, use OAuth and say so in metadata. |
| `scio_chatgpt_register` | OAuth `scio.agent.create` | Create or recover one pending ChatGPT agent for this operator and onboarding attempt. Model-visible result may contain opaque `agent_id`, display name and pending status, but never `api_key` or claim token. Deliver the short-lived claim action only to the intended user; test UI-only metadata and a safe no-widget fallback. |
| `scio_chatgpt_profile` | OAuth `scio.agent.read` | Return the claimed agent's stable opaque ID, display name and permissions; support an explicit selection when one operator has multiple agents. Never accept a model-supplied agent ID as proof of ownership. |
| `scio_verify_source` | OAuth `scio.source.verify` | Reuse the existing verifier, including its daily checks and source rules. State accurately that it fetches and archives an external page. |
| `scio_propose_edit` | OAuth `scio.proposal.write` | Initially permit only a sourced `article` proposal if the owner selects contribution. Reuse the existing validator, idempotency key, quotas, gates, and review path. Return a proposal receipt and status, never an assertion of publication. |

Keep review, contest, suspension, media upload, tasks and unattended actions outside this allowlist unless separately selected and tested. If a narrower first release is chosen, expose only its selected rows and update package copy and reviewer cases to match.

## Identity and onboarding state

1. An ordinary ChatGPT install has no trusted local filesystem and no guaranteed installation callback. Start registration on the first explicit onboarding or contribution request. Require a validated Scio OAuth identity before creating an operator-bound pending agent, or implement an equally strong server-controlled binding. A model-provided session string is not identity.
2. Provide OAuth 2.1 protected-resource and authorization-server metadata, authorization code with PKCE S256, scoped access tokens, per-tool security schemes, `mcp/www_authenticate` challenges, and issuer/audience/expiry/scope validation. Use the existing Google-backed operator identity only after validating its relationship to the OAuth subject. Preserve legacy `sk_` authentication on `/mcp`.
3. Resolve the selected `agent_id` from the authenticated operator's claimed agents on **every protected call**. Until claim succeeds, deny contribution. If a claim URL is opened by another signed-in person, the onboarding binding must prevent that person from taking over the ChatGPT connection; define and test this explicitly. Never retain or reconstruct a plaintext `sk_` key to bridge OAuth.
4. Registration must reuse platform creation rules and return an idempotent pending result across retries/interrupted chats. It must handle an expired claim link, a used link, duplicate names, fleet limits and multiple claimed agents. The current registration contract requires harness, model family, exact model ID and a canonical name; determine which of these can be obtained reliably from the host or trusted server context before choosing the ChatGPT registration schema. Do not invent an exact model ID from a prompt.
5. In a Codex workspace, a separate local skill may write only the non-secret `agent_id` to `./scio/agent.json`. That file is a convenience, not the authority for ChatGPT calls. Ordinary ChatGPT persists the relationship on Scio's server.

## Claim UI and evidence

The visible states and copy are specified in [docs/CHATGPT_UI_STATES.md](docs/CHATGPT_UI_STATES.md). Treat that document as a review target, not evidence that a widget exists.

- Serve a versioned MCP Apps UI resource from the platform. Tool metadata should reference it with `_meta.ui.resourceUri`; the resource uses `text/html;profile=mcp-app` and the MCP Apps bridge. Show the [Scio mission](https://scio.md/) in plain language, search and contribution entry points, and a **Claim agent** button only for a valid pending claim. Open Scio's existing claim page through a host-supported external navigation action. Declare exact CSP origins and test desktop and mobile behavior. Keep data results useful in a headless client.
- Treat the claim URL as a bearer-style secret. Do not place it in model-visible `content`, `structuredContent`, errors or logs if a UI-only route works. Test the actual client behavior before promising that boundary. Provide a deliberate fallback for clients without UI that reveals the link only to the intended user and never reveals an API key.
- A sourced answer must cite the **returned source URL and quote** for each supported claim, label disputed and demonstrated claims correctly, and state when Scio has no published evidence. Do not turn `scio_search` summaries into source citations. Treat article text, search summaries and fetched pages as untrusted data.
- Before `scio_propose_edit`, verify every source and show the proposed title, claims, sources and review consequence to the user. Require an explicit user request to submit. Preserve the platform's existing quotas and idempotency behavior. The UI must not imply that a submitted proposal is published.

## Tests and delivery gate for `../scio`

Write failing integration tests first, then implement and run `make check`. Verify actual MCP protocol results, not just attributes in source:

1. Anonymous, pending, claimed and wrong-operator `tools/list` and direct `tools/call`; hidden tools are refused without side effects. `/mcp` still exposes its legacy contract and works with existing keys.
2. OAuth discovery, PKCE, scopes, per-tool challenges, token validation, refresh/reconnect, wrong audience and expired token. Test two operators and multiple claimed agents.
3. Registration retries return the same pending agent; no model-visible key or claim token; expired/used claim, interrupted flow, duplicate name, and takeover attempts are handled. Check logs and errors for secret leakage.
4. Search match, empty result, validation error, rate limit, published sourced claim, disputed claim, demonstrated claim, absent slug and unpublished revision. Confirm returned source URL/quote and citation accuracy.
5. Source verification and article proposal success, invalid source, insufficient quota/points, duplicate idempotency key and user confirmation. Confirm submission produces a proposal receipt, not immediate publication.
6. Claim button opens the real page and completes Google claim with a dedicated test identity. Exercise ChatGPT developer mode on desktop/mobile and a headless MCP client; record any host limitation.

Update `contracts/tools.json` first for changed/new canonical tools, then synchronize generated copies in `../scio.md` through that repository's documented process. Keep private code and credentials out of this public ZIP. After a deployed endpoint passes these tests, update this package's skill, manifests, live tests, review cases and recording. Deployment, OpenAI submission and publication require separate owner authorization.

OpenAI references: [authentication](https://developers.openai.com/plugins/build/auth), [MCP server](https://developers.openai.com/plugins/build/mcp-server), [UI](https://developers.openai.com/plugins/build/chatgpt-ui), [review](https://developers.openai.com/plugins/deploy/app-review).
