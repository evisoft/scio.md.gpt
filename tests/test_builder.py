"""Check the archive builder's file boundary."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/build.py"
SPEC = importlib.util.spec_from_file_location("build_plugin", SCRIPT)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class BuilderTests(unittest.TestCase):
    def test_allowlisted_symlink_cannot_pull_in_external_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            outside = root / "outside-secret"
            outside.write_text("private material", encoding="utf-8")
            (root / "plugin.json").symlink_to(outside)
            with patch.object(builder, "ROOT", root), patch.object(builder, "FILES", ("plugin.json",)):
                with self.assertRaisesRegex(ValueError, "symlink"):
                    builder.main()
            self.assertFalse((root / "dist/scio-chatgpt-plugin.zip").exists())

    def test_allowlisted_file_with_oauth_secret_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plugin.json").write_text('access_token = "oauth-test-secret-value"')
            with patch.object(builder, "ROOT", root), patch.object(builder, "FILES", ("plugin.json",)):
                with self.assertRaisesRegex(ValueError, "possible secret"):
                    builder.main()
            self.assertFalse((root / "dist/scio-chatgpt-plugin.zip").exists())

    def test_allowlisted_file_with_raw_jwt_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plugin.json").write_text(
                "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LWFjY291bnQifQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                encoding="utf-8",
            )
            with patch.object(builder, "ROOT", root), patch.object(builder, "FILES", ("plugin.json",)):
                with self.assertRaisesRegex(ValueError, "possible secret"):
                    builder.main()
            self.assertFalse((root / "dist/scio-chatgpt-plugin.zip").exists())


if __name__ == "__main__":
    unittest.main()
