import json
import re
import unittest
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/scio"
PACKAGE_FILES = (
    "plugin.json",
    "mcp.json",
    "LICENSE",
    "assets/scio.svg",
    "skills/scio/SKILL.md",
    "skills/scio/agents/openai.yaml",
    "skills/scio/assets/claim.schema.json",
    *(f"skills/scio/references/{name}.md" for name in (
        "actions", "connect", "maintain", "markdown", "research", "review",
        "rules", "security", "style", "team", "translate", "write",
    )),
)
TOOLS_IN_WORKFLOW = (
    "scio_whoami", "scio_get_rules", "scio_search", "scio_get_article", "scio_get_claims",
    "scio_get_history", "scio_diff", "scio_get_tasks", "scio_verify_source",
    "scio_propose_edit", "scio_get_panel", "scio_review", "scio_contest",
    "scio_reserve_gap", "scio_request_article", "scio_discuss", "scio_get_discussion",
    "scio_report", "scio_suspend", "scio_upload_media", "scio_feedback",
)


class PackageTests(unittest.TestCase):
    def test_remote_oauth_mcp_only(self):
        config = json.loads((ROOT / "mcp.json").read_text())
        self.assertEqual(config["$schema"], "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json")
        self.assertEqual(config["mcpServers"], {"scio": {"type": "streamable-http", "url": "https://scio.md/connect"}})

    def test_listing_limits_and_assets(self):
        manifest = json.loads((ROOT / "plugin.json").read_text())
        self.assertEqual(manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(manifest["version"], "0.3.0")
        self.assertRegex(manifest["name"], r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
        self.assertLessEqual(len(manifest["name"]), 64)
        self.assertRegex(manifest["version"], r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
        self.assertNotIn("hooks", manifest["extensions"]["com.openai"])
        self.assertTrue(manifest["extensions"]["com.openai"]["publication"]["release_notes"])
        self.assertNotIn("review", manifest["extensions"]["com.openai"])
        interface = manifest["extensions"]["com.openai"]["interface"]
        self.assertIn(interface["category"], {
            "Productivity", "Creativity", "Developer Tools", "Business & Operations",
            "Data & Analytics", "Communication", "Education & Research", "Security",
            "Finance", "Healthcare", "Travel", "Entertainment", "Other",
        })
        self.assertLessEqual(len(interface["displayName"]), 30)
        self.assertLessEqual(len(interface["shortDescription"]), 30)
        self.assertLessEqual(len(interface["longDescription"]), 4000)
        self.assertLessEqual(len(interface["developerName"]), 80)
        for key in ("displayName", "shortDescription", "developerName"):
            self.assertEqual(interface[key], interface[key].strip())
            self.assertFalse(any(unicodedata.category(char) in {"Cc", "Cf", "Zl", "Zp"} for char in interface[key]))
            self.assertNotIn("\n", interface[key])
        for statement in ("OAuth", "review", "proposals", "one point", "agent-written"):
            self.assertIn(statement, interface["longDescription"])
        prompts = interface["defaultPrompt"]
        self.assertLessEqual(len(prompts), 3)
        normalized = [" ".join(unicodedata.normalize("NFKC", prompt).split()).casefold() for prompt in prompts]
        self.assertEqual(len(set(normalized)), len(prompts))
        self.assertTrue(all(prompt.strip() and len(prompt) <= 128 and "@" not in prompt and "\n" not in prompt for prompt in prompts))
        self.assertLessEqual(len(interface["capabilities"]), 20)
        self.assertTrue(all(label.strip() and len(label) <= 120 for label in interface["capabilities"]))
        for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
            url = interface[key]
            parts = urlsplit(url)
            self.assertEqual(parts.scheme, "https")
            self.assertTrue(parts.hostname)
            self.assertFalse(parts.username or parts.password)
            self.assertLessEqual(len(url), 1024)
        self.assertRegex(interface["brandColor"], r"^#[0-9A-Fa-f]{6}$")
        self.assertLessEqual(self._relative_luminance(interface["brandColor"]), 0.475)
        for key in ("logo", "composerIcon"):
            self.assertTrue(interface[key].startswith("./assets/"))
            icon = ET.parse(ROOT / interface[key][2:]).getroot()
            self.assertEqual(icon.attrib["width"], icon.attrib["height"])
            self.assertGreaterEqual(int(icon.attrib["width"]), 48)
            self.assertLessEqual((ROOT / interface[key][2:]).stat().st_size, 5 * 1024 * 1024)

    @staticmethod
    def _relative_luminance(color):
        channels = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
        return sum(weight * value for weight, value in zip((0.2126, 0.7152, 0.0722), linear))

    def test_platform_contract_and_paged_review(self):
        contract_file = ROOT.parent / "scio" / "contracts" / "tools.json"
        if not contract_file.exists():
            self.skipTest("sibling Scio platform contract is not available")
        contract = json.loads(contract_file.read_text())
        tools = {tool["name"]: tool for tool in contract["tools"]}
        self.assertEqual(set(TOOLS_IN_WORKFLOW), set(tools) - {"scio_register"})
        for name in set(TOOLS_IN_WORKFLOW) - {"scio_search", "scio_get_rules"}:
            self.assertEqual(tools[name]["auth"], "bearer")
        self.assertFalse(tools["scio_get_tasks"]["readOnly"])
        self.assertFalse(tools["scio_get_article"]["readOnly"])
        self.assertTrue(tools["scio_contest"]["destructive"])
        self.assertTrue(tools["scio_suspend"]["destructive"])
        panel = tools["scio_get_panel"]
        self.assertIn("cursor", panel["input"]["properties"])
        self.assertIn("next_cursor", panel["output"]["properties"])
        review = (SKILL / "references/review.md").read_text()
        self.assertIn("next_cursor", review)
        self.assertIn("every page", review)
        self.assertIn("ordinal", review)
        claim_schema = json.loads((SKILL / "assets/claim.schema.json").read_text())
        live_claim = tools["scio_propose_edit"]["input"]["properties"]["claims"]["items"]
        self.assertEqual(set(claim_schema["properties"]), set(live_claim["properties"]))
        self.assertEqual(set(claim_schema["required"]), set(live_claim["required"]))
        connector = ROOT.parent / "scio" / "src/Scio.Api/Mcp/ConnectorSurface.cs"
        if connector.exists():
            self.assertIn('HiddenTool = "scio_register"', connector.read_text())

    def test_skill_is_portable_and_references_resolve(self):
        skill = (SKILL / "SKILL.md").read_text()
        agent_metadata = (SKILL / "agents/openai.yaml").read_text()
        self.assertRegex(agent_metadata, r"(?m)^interface:\n  display_name: .+\n  short_description: .+$")
        bundled = "\n".join((ROOT / name).read_text() for name in PACKAGE_FILES if name.endswith(".md"))
        for forbidden in ("SCIO_API_KEY", "scio_bridge", "scio_chatgpt_register", "scio_register_reader", "scio_get_public_article", "scio-local", "workdir(", "Claude Code", "claude.ai", "Cowork"):
            self.assertNotIn(forbidden, bundled)
        for tool in TOOLS_IN_WORKFLOW:
            self.assertIn(tool, bundled)
        for name in PACKAGE_FILES:
            if not name.endswith(".md"):
                continue
            path = ROOT / name
            prose = re.sub(r"```.*?```", " ", path.read_text(), flags=re.S)
            prose = re.sub(r"`[^`\n]*`", " ", prose)
            for target in re.findall(r"\]\(([^)#]+)(?:#[^)]+)?\)", prose):
                if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                    continue
                resolved = (path.parent / target).resolve()
                self.assertTrue(resolved.is_relative_to(SKILL.resolve()), (name, target))
                self.assertTrue(resolved.exists(), (name, target))
        self.assertIn('part: "numbers"', skill)
        self.assertIn("next_cursor", skill)
        self.assertIn("no public article page", skill)
        server = json.loads((ROOT / "mcp.json").read_text())["mcpServers"]["scio"]
        self.assertIn('value: "scio"', agent_metadata)
        self.assertIn(f'url: "{server["url"]}"', agent_metadata)
        schema = json.loads((SKILL / "assets/claim.schema.json").read_text())
        self.assertEqual(schema["type"], "object")

    def test_public_archive_exact_and_without_runtime(self):
        archive = ROOT / "dist/scio-chatgpt-plugin.zip"
        self.assertTrue(archive.exists(), "build the archive first")
        with ZipFile(archive) as zip_file:
            self.assertLessEqual(archive.stat().st_size, 100 * 1024 * 1024)
            self.assertEqual(tuple(zip_file.namelist()), PACKAGE_FILES)
            for name in PACKAGE_FILES:
                self.assertEqual(zip_file.read(name), (ROOT / name).read_bytes())
            self.assertFalse(any(name.endswith(".py") or "scio-search" in name for name in zip_file.namelist()))


if __name__ == "__main__":
    unittest.main()
