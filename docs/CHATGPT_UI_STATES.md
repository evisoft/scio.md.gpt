# Proposed Scio UI states for ChatGPT

**Superseded for the first release:** the owner removed OAuth, Claim and contribution. Current scope is in [SERVER_CHANGES.md](../SERVER_CHANGES.md); a search/read UI, if added, must not show the old actions.

**Status:** product and server specification. No widget is implemented or packaged here. The first-release tool selection is open. Ordinary ChatGPT does not run a plugin install hook or show a guaranteed plugin homepage; an MCP Apps card appears when a suitable tool result invokes its server-hosted UI resource. The listing and short skill can introduce Scio before that point.

The Scio platform should host and version the UI resource. The public ZIP needs only its portable manifest, remote MCP configuration, icon and short skill. The widget uses the standard MCP Apps bridge and exact CSP domains described in OpenAI's [UI build guide](https://developers.openai.com/plugins/build/chatgpt-ui) and [UI reference](https://developers.openai.com/plugins/reference).

## Copy and states

| State | Visible content | Available action | Server fact that controls it |
|---|---|---|---|
| Introduction | “We are building the knowledge library for superintelligence.” Follow with: “Search Scio's coverage and evidence. Agents can propose sourced articles; proposals are reviewed before publication.” | **Search Scio**; **Contribute an article** only when onboarding exists | Tool availability from the actual endpoint. Do not show an unsupported action. |
| Search matches | Topic, article title, language, coverage state and summary. Show a source label only after a claim-reading tool returns a source URL and quote. | Open published claims/evidence when available | Search and published-claim results. |
| No match | “No matching Scio article was found.” | Search again; optionally begin a contribution request | Empty search result. Never invent a citation or anonymous gap bounty. |
| Account needed | Brief explanation that claiming an agent links the person's Scio identity to contributions. | **Connect Scio** through the host's OAuth flow | Missing/expired OAuth token and a supported auth challenge. |
| Pending claim | Agent display name and opaque ID; short statement that the person will take responsibility for this agent's proposals. | **Claim agent** opens the server-supplied `scio.md/claim/...` page | Authenticated pending registration bound to this operator; unexpired, unused claim action. |
| Claim completed | Claimed agent name and ID, plus permission/point status if the profile tool returns it. | Continue to source checks and drafting | Scio server verifies the Google claim and OAuth operator/agent relationship. |
| Draft ready | Proposed title, every claim, its source URL and exact quote, verification status, and explanation that a submission enters review. | **Submit proposal** only after the person explicitly confirms | Authenticated claimed agent, valid sources, prepared proposal and current quota. |
| Submitted | Proposal ID and current status. | View status if a supported read tool exists | Actual proposal receipt. Never label it published without a publication result. |
| Expired or refused | Clear reason appropriate to the state: claim link expired, wrong account, missing permission, invalid source, quota, or network error. | Retry only a safe/idempotent step; otherwise return to Scio | Structured server error. Do not expose credentials or internal tokens. |

## Claim button boundary

The button is shown only after the ChatGPT-specific registration operation succeeds. The widget receives the claim action through a tested UI-only result channel, and invokes a host-supported external navigation API. The claim page itself handles Google sign-in and the claim. The claim token is a bearer-style secret: keep it out of model-visible result fields, analytics, screenshots, and error strings. If a host cannot support this safely, replace the button with a clearly labeled user-facing fallback only after testing that fallback. Never use legacy `scio_register` in this flow because it exposes an API key.

The widget must re-query server state after returning from the claim page; an open browser tab or successful redirect alone is not proof that the correct person claimed the agent. A different operator's claim must not unlock the original ChatGPT connection. All protected tool calls recheck the operator/agent relationship on the server.

## Acceptance observations

1. Test each visible state in ChatGPT developer mode on desktop and mobile where available. Record screenshots or a redacted video of the actual host, not a mockup presented as a working integration.
2. Verify the card remains useful with keyboard and text resizing, follows host light/dark colors, and does not put nested scrolling inside a small card.
3. Test with UI unavailable: search and evidence remain understandable from tool `content`/`structuredContent`; onboarding returns a safe path for the intended user without an API key.
4. Confirm `Claim agent` opens only the trusted Scio claim origin, including on mobile, and that expired or already-used links return to a recoverable state.
5. Confirm search summaries and source previews are rendered as untrusted content and cannot trigger registration or proposal submission by containing instructions.

The [server handoff](../SERVER_FULL_EXPERIENCE.md) defines the proposed tools and OAuth checks. The [full-flow review cases](../REVIEW_FULL_EXPERIENCE.md) define user prompts that must pass before this copy can be advertised.
