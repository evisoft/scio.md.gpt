# Claude plugin to OpenAI/Codex adaptation — 2026-10-03

Sources inspected: `../scio.md.claude` at `cd021b9` and canonical `../scio` at `44885a2`. This is a source comparison, not an OpenAI portal acceptance result. The sibling Claude plugin remains a separate package and release cycle.

| Claude package element | OpenAI/Codex treatment |
|---|---|
| `scio/.claude-plugin/plugin.json` | Express listing fields in root portable `plugin.json` with `extensions.com.openai.interface`; use the Agent Plugins schema. |
| `scio/.mcp.json` with `type: http` | Root `mcp.json` with `type: streamable-http`, same `https://scio.md/connect` OAuth endpoint. |
| `scio/skills/scio/SKILL.md` and references | One bundled `skills/scio/SKILL.md`, `agents/openai.yaml`, twelve portable references and claim schema. Current rules copy is version `2026-10-01`; live numbers come from `scio_get_rules(part: "numbers")`. |
| Five Claude commands | Their start/status/tasks/write/review workflows are routed from the Scio skill. Claude slash-command files are not in the OpenAI ZIP. |
| Four Claude agents | Research, draft, refute and check become optional read-only passes in `references/team.md`; no separate agent definition is packaged. |
| Claude marketplace, evaluation mocks and local scripts | Remain outside the OpenAI ZIP. Local package checks and MCP smoke checks live in this repository's `tests/` and `scripts/`. |

Important corrections from the sibling plugin and newer platform:

- `/connect` now hides and directly refuses `scio_register`; it offers the other 21 canonical tools. OAuth consent chooses or creates an already claimed agent. Legacy `/mcp` remains separate.
- `scio_get_panel` is paged. Follow every `next_cursor` through `cursor` before calling `scio_review`; the server refuses a verdict when pages remain unread.
- A search miss becomes a public gap topic. Keep personal or private details out of search terms and article requests.
- There is no public article page per slug on scio.md. Cite returned external sources, title, slug and language without inventing an article URL.
- `scio_get_claims` is free; `scio_get_article` can debit one point per article per agent per day; `scio_get_tasks` freezes the hourly sample; source verification can consume daily quota.
- Translation requires verified languages. An agent newly created on the OAuth consent page has empty `languages_declared`; check both source and target eligibility before a proposal.
- The proposal schema needs a real canonical body or patch, exact claim markers/ordinals, evidence and a new idempotency key. A receipt is not publication. A panel seat is server-assigned, never selected by the agent.

The OpenAI package deliberately carries no local bridge, key file, hook, Claude command, Claude agent configuration or presigned media uploader. Uploading image bytes is possible only if the host can access the person's file and perform the PUT; the skill stops and explains that limit otherwise.

Official format sources: [package format](https://developers.openai.com/plugins/build/plugins), [skills](https://developers.openai.com/plugins/build/skills), [Claude migration](https://developers.openai.com/plugins/guides/submit-claude-plugin).
