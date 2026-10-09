#!/usr/bin/env python3
"""Build an explicit, deterministic public plugin archive."""

import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "plugin.json",
    "mcp.json",
    "LICENSE",
    "assets/scio.svg",
    "skills/scio/SKILL.md",
    "skills/scio/agents/openai.yaml",
    "skills/scio/assets/claim.schema.json",
    "skills/scio/references/actions.md",
    "skills/scio/references/connect.md",
    "skills/scio/references/maintain.md",
    "skills/scio/references/markdown.md",
    "skills/scio/references/research.md",
    "skills/scio/references/review.md",
    "skills/scio/references/rules.md",
    "skills/scio/references/security.md",
    "skills/scio/references/style.md",
    "skills/scio/references/team.md",
    "skills/scio/references/translate.md",
    "skills/scio/references/write.md",
)
FORBIDDEN_NAMES = (".app.json", ".mcp.json", "hooks/", "scripts/", "key/", ".env")
SECRET_PATTERNS = (
    re.compile(rb"sk_[A-Za-z0-9_-]{16,}"),
    re.compile(rb"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{16,}\b"),
    re.compile(rb"\bya29\.[A-Za-z0-9._-]{16,}\b"),
    re.compile(rb"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
    re.compile(rb"(?i)\b(?:access_token|refresh_token|client_secret|api_key)\b\s*[:=]\s*['\"]?[^\s'\"{},;]{12,}"),
    re.compile(rb"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._~-]{16,}"),
)


def main() -> int:
    contents = {}
    for name in FILES:
        if Path(name).is_absolute() or name.startswith(FORBIDDEN_NAMES) or any(part in ("..", "") for part in Path(name).parts):
            raise ValueError(f"unsupported archive path: {name}")
        path = ROOT / name
        parts = Path(name).parts
        if any((ROOT / Path(*parts[:index])).is_symlink() for index in range(1, len(parts) + 1)):
            raise ValueError(f"symlink in archive path: {name}")
        data = path.read_bytes()
        if any(pattern.search(data) for pattern in SECRET_PATTERNS):
            raise ValueError(f"possible secret in {name}")
        contents[name] = data

    output = ROOT / "dist" / "scio-chatgpt-plugin.zip"
    output.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in FILES:
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, contents[name])
    with zipfile.ZipFile(output) as archive:
        if tuple(archive.namelist()) != FILES:
            raise ValueError("archive content differs from allowlist")
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
