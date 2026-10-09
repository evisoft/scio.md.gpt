# Scio ChatGPT plugin

Read [AGENTS.md](AGENTS.md) first. It is the working brief and acceptance checklist for this sibling project. Read [HANDOFF.md](HANDOFF.md) for the findings already confirmed and the proposed sequence.

The owner's current choice is the full OAuth-connected Scio workflow at `https://scio.md/connect`: search, article reading, source verification, proposals, translations, server-assigned panel reviews and other authorized tools. The person chooses or creates an agent on Scio's consent page. An agent cannot pick its own review seat. [SERVER_CHANGES.md](SERVER_CHANGES.md) records remaining server-side metadata and public-review work. The earlier search/read and anonymous-reader scopes are superseded.

Read [docs/OPENAI_PLUGINS.md](docs/OPENAI_PLUGINS.md) and the [29-page official review](docs/OFFICIAL_PAGES.md) before changing the package, MCP requirements, or review materials. They summarize the OpenAI Plugins documentation checked on 2026-10-02 and flag conflicting official guidance; verify the linked live pages before implementation or submission.

For the current package, also read [docs/OPENAI_REQUIREMENTS.md](docs/OPENAI_REQUIREMENTS.md) and [docs/CLAUDE_ADAPTATION.md](docs/CLAUDE_ADAPTATION.md). The existing `../scio.md.claude` plugin supplies provider-neutral Scio workflow knowledge; OpenAI uses a portable manifest, `agents/openai.yaml`, and bundled skill references rather than Claude commands or agents. The current `/connect` source excludes legacy `scio_register`.

The Scio product has three relevant source repositories beside this folder:

- `../scio.md` is the **public, existing companion plugin and skill**. Its `skills/scio/` material and `docs/HOW_IT_WORKS.md` explain the user workflows. Its current root package is tailored to several local agent harnesses, so treat it as reference and compatibility surface, not the ChatGPT submission ZIP.
- `../scio.md.claude` is the **separate Claude OAuth plugin**. Its Markdown workflows, package tests and eval cases inform this package. Its `.claude-plugin` manifest, commands and agents do not belong in the portable OpenAI ZIP.
- `../scio` is the **private hosted platform** and canonical server contract. Read `../scio/AGENTS.md` before editing it. Its `contracts/tools.json` and API implementation govern the live MCP tools, authentication, rules, and data. Never copy private code, credentials, database contents, or internal operational details into a public package.

Work toward a reviewable, submission-ready ZIP and tested remote MCP experience. Keep edits for this integration in this folder where possible. Any change to `../scio` or `../scio.md` needs its own focused tests and compatibility checks. Record precisely what remains for the owner to do in the OpenAI portal; do not submit or publish on their behalf.
