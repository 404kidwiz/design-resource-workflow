import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkout = self.root / "checkout"
        (self.checkout / "references").mkdir(parents=True)
        for name in ("install.py", "SKILL.md", "references/catalog.md"):
            shutil.copy2(REPO / name, self.checkout / name)
        self.home = self.root / "home"
        self.home.mkdir()

    def run_installer(self, *args, success=True):
        result = subprocess.run(
            [sys.executable, str(self.checkout / "install.py"), "--home", str(self.home), *args],
            text=True, capture_output=True, timeout=10,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def test_dry_run_then_install_verify_and_repeat(self):
        self.run_installer("--dry-run")
        self.assertEqual(list(self.home.iterdir()), [])
        self.run_installer()
        self.run_installer("--verify")
        self.run_installer()
        for folder in (
            ".skills", ".hermes/skills", ".codex/skills", ".claude/skills",
            ".cursor/skills", ".gemini/skills", ".config/opencode/skills",
            ".opencode/skills", ".openclaude/skills", ".grok/skills",
            ".zcode/skills", ".agents/skills",
        ):
            dest = self.home / folder / "design-resource-workflow"
            self.assertEqual((dest / "SKILL.md").read_bytes(), (self.checkout / "SKILL.md").read_bytes())
            self.assertEqual((dest / "references/catalog.md").read_bytes(), (self.checkout / "references/catalog.md").read_bytes())

    def test_existing_user_files_are_not_overwritten(self):
        dest = self.home / ".claude/skills/design-resource-workflow"
        dest.mkdir(parents=True)
        (dest / "SKILL.md").write_text("user-owned\n")
        output = self.run_installer("--tools", "claude", success=False)
        self.assertIn("CONFLICT", output)
        self.assertEqual((dest / "SKILL.md").read_text(), "user-owned\n")

    def test_managed_copy_updates_only_if_unchanged(self):
        args = ("--tools", "claude", "--mode", "copy")
        self.run_installer(*args)
        dest = self.home / ".claude/skills/design-resource-workflow"
        (self.checkout / "references/catalog.md").write_text("revised catalog\n")
        self.assertIn("STALE", self.run_installer(*args, "--verify", success=False))
        self.run_installer(*args)
        self.assertEqual((dest / "references/catalog.md").read_text(), "revised catalog\n")
        (dest / "SKILL.md").write_text("local edit\n")
        output = self.run_installer(*args, success=False)
        self.assertIn("CONFLICT", output)
        self.assertEqual((dest / "SKILL.md").read_text(), "local edit\n")

    def test_broken_symlink_is_not_replaced(self):
        dest = self.home / ".codex/skills/design-resource-workflow"
        dest.parent.mkdir(parents=True)
        try:
            dest.symlink_to(self.root / "missing", target_is_directory=True)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        output = self.run_installer("--tools", "codex", success=False)
        self.assertIn("CONFLICT", output)
        self.assertTrue(dest.is_symlink())

    def test_managed_copy_rejects_symlinked_file_even_if_hash_matches(self):
        args = ("--tools", "claude", "--mode", "copy")
        self.run_installer(*args)
        dest = self.home / ".claude/skills/design-resource-workflow"
        external = self.root / "external-skill.md"
        shutil.copy2(dest / "SKILL.md", external)
        (dest / "SKILL.md").unlink()
        try:
            (dest / "SKILL.md").symlink_to(external)
        except OSError as error:
            self.skipTest(f"symlink unavailable: {error}")
        (self.checkout / "SKILL.md").write_text("new version\n")
        output = self.run_installer(*args, success=False)
        self.assertIn("CONFLICT", output)
        self.assertEqual(external.read_bytes(), (REPO / "SKILL.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
