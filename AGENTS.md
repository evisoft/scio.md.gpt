# Scio for ChatGPT and Codex: agent brief

## Objective

Build a **separate, submission-ready OpenAI plugin package** in this folder. It must connect to Scio through a remote HTTPS MCP server and give ChatGPT users a useful, reliable, source-backed experience. Finish the package, tests, reviewer materials, and a precise list of operator-only portal steps. The owner asked for readiness to submit, not submission or publication.

## Current owner choice: full OAuth workflows

On 2026-10-03 the owner reported that Scio's OAuth MCP connector works in ChatGPT. The latest request expands this plugin from search and reading to writing, assigned panel reviews, and the other server-supported Scio functions. Use `https://scio.md/connect` and its actual MCP tools. Scio's consent page lets the person choose an existing agent or create one; creation is not silent. An agent cannot choose or claim its own panel seat: Scio draws assignments, which the plugin can inspect and review. Explain costs, quota, public effects and authorization before consequential calls. [SERVER_CHANGES.md](SERVER_CHANGES.md) records remaining server metadata and public-review work. This direction supersedes the narrower search/read scope and the 2026-10-02 anonymous-reader proposal.

This is a sibling project so its public ZIP and release cycle stay isolated from the existing multi-harness plugin. It is not a new source of truth for Scio's API, tool schemas, rules, identity, or hosted behavior.

## Saved OpenAI documentation research

Read [docs/OPENAI_PLUGINS.md](docs/OPENAI_PLUGINS.md) for the 2026-10-02 synthesis of official plugin requirements and Scio-specific decision points. [docs/OFFICIAL_PAGES.md](docs/OFFICIAL_PAGES.md) records findings for all 29 OpenAI pages requested by the owner, including conflicting guidance about annotation justifications. These notes are a snapshot, not a replacement for the linked OpenAI documentation; recheck the live pages before implementing or submitting. The public submission rules can be narrower than the general local-plugin package capabilities.

The 2026-10-03 [OpenAI requirements audit](docs/OPENAI_REQUIREMENTS.md) and [Claude adaptation map](docs/CLAUDE_ADAPTATION.md) reflect the later full-workflow package. `../scio.md.claude` is an existing sibling plugin; read its `CLAUDE.md` and `scio/skills/scio/` for portable workflow knowledge, but do not copy its manifest, commands, agents or runtime format into this ZIP. The current server source at `../scio` exposes 21 tools on `/connect`, excluding `scio_register`.

## Source-of-truth map

| Area | Location | Use |
|---|---|---|
| Existing public companion plugin | `../scio.md` | Read `README.md`, `skills/scio/SKILL.md`, `docs/HOW_IT_WORKS.md`, `docs/openai-submission.md`, and the current manifests. Reuse product knowledge and assets selectively. Its local Python bridge, hooks, and scripts are for other harnesses; they cannot be assumed to run in ordinary ChatGPT. |
| Existing Claude OAuth plugin | `../scio.md.claude` | Read `CLAUDE.md`, `scio/skills/scio/`, package tests and evals for portable source, proposal and panel workflows. Keep its Claude manifest, commands and agents out of the OpenAI ZIP. |
| Private hosted platform | `../scio` | Read its `AGENTS.md` first, then `contracts/tools.json`, `src/Scio.Api/Mcp/ScioTools.cs`, auth and HTTP code, tests, and deployment guidance. It owns `https://scio.md/mcp`, `/v1`, authentication, tool exposure, and canonical contracts. Keep private source and credentials out of this public package. |
| This folder | `.` | Own the OpenAI-specific manifest, remote MCP configuration, focused skill, assets, packaging and validation, review cases, and submission instructions. |

Check the current worktree state and applicable instructions in each repository before making changes. If a platform tool contract changes, update the canonical contract in `../scio` and synchronize its copies in `../scio.md` through that repository's documented process. Do not hand-edit generated copies.

## Product scope and decision points

1. Start with a concrete ChatGPT use case: search Scio, inspect evidence when the current account permits it, and answer with underlying sources and honest coverage limits. Test what works anonymously; do not assume article reads work without a key or are free.
2. Audit the remote MCP server's complete `tools/list`, descriptions, schemas, security schemes, annotations, and errors as ChatGPT sees them. The platform currently advertises many contribution tools. If that makes the first experience hard to review or unsafe, expose a stable, narrowly scoped remote endpoint or another server-side allowlist **in `../scio`**; do not create a second implementation of Scio business rules here.
3. Decide and implement supported user authentication before promising account-specific reads or actions. Existing Scio `sk_` bearer keys are not a ChatGPT sign-in flow. OpenAI's current guidance expects OAuth 2.1 for authenticated MCP access, with discovery, PKCE, scopes, per-tool security schemes, and authorization enforced by the server. Preserve existing agent keys and legacy clients. Do not place keys in prompts, ZIPs, manifests, logs, or test fixtures.
4. Cover contribution, assigned reviews, contests, suspension and media upload only through their real OAuth-backed tools, current permissions and rules. Make the user-visible decision and confirmation match the action's cost and effect; test reviewer cases with a dedicated identity. Never use legacy `scio_register` as a ChatGPT onboarding path because its response includes an API key.
5. A plugin ZIP is the reviewed artifact. Build it from an explicit file list in this folder. Do not upload either sibling repository wholesale. Keep local hooks, `.app.json` references, local stdio servers, and unrelated harness assets out of a public submission ZIP unless current OpenAI rules explicitly allow them.

## Required deliverables

- A portable `plugin.json` and remote `mcp.json` for the OpenAI directory, with a narrow, accurate description, valid listing URLs, icons, and at most the current allowed number of starter prompts.
- A small Agent Skills-format skill if it improves use of the MCP tools. It must describe the ChatGPT workflow actually supported by the remote server, without dependencies on local project files, Python, hooks, or a launcher. Avoid instructions to invoke Scio for every factual question regardless of user intent.
- A reproducible build command that creates a clean ZIP and checks its contents for secrets and unsupported components.
- Automated contract/package checks and meaningful end-to-end MCP tests, including anonymous/authenticated behavior as applicable, source citations, empty results, errors, and confirmation boundaries. Test in ChatGPT developer mode on desktop and mobile where possible; record what cannot be tested locally.
- Five positive and three negative review cases that match the **actual exposed tools**; reviewer-safe sample data and a plan for a reachable demo account when sign-in is required; a reviewer-accessible demo recording; privacy/support/terms URLs; domain challenge setup instructions; and a submission checklist.
- A short `README.md` explaining build, test, deployment dependencies, and exact remaining operator portal actions. State separately what is validated locally, what is deployed, and what OpenAI has reviewed. Do not call a package accepted before the portal approves it.

## Verification and release boundaries

Follow TDD and `make check` in `../scio` for platform changes. Follow the existing security, contract-sync, and manifest checks in `../scio.md` for companion changes. Test old clients when changing shared authentication or MCP metadata. A ChatGPT-specific endpoint must coexist with the existing `/mcp` behavior unless an intentional, tested compatibility migration is agreed.

Do not deploy the platform, submit the ZIP, publish the plugin, provide reviewer credentials, or push a release merely because the package is ready. Prepare those steps and obtain the owner's final authorization where needed. No developer account or operator identity should be used for reviewer testing; create a dedicated test identity and sample data through the normal product flow.

## Current official references (recheck before implementation/submission)

- Submission: https://developers.openai.com/plugins/deploy/submission
- Package format: https://developers.openai.com/plugins/build/plugins
- Guidelines: https://developers.openai.com/plugins/plugin-guidelines
- Authentication: https://developers.openai.com/plugins/build/auth
- Testing: https://developers.openai.com/plugins/deploy/connect-chatgpt
- Claude plugin migration: https://developers.openai.com/plugins/guides/submit-claude-plugin

OpenAI changes these rules. Use the current official pages and report any drift from this brief before packaging.
