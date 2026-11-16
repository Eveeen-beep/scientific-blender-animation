"""Offline package metadata and local Markdown link checks."""

from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def test_skill_frontmatter_has_name_and_description(self):
        source = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", source, re.DOTALL)
        self.assertIsNotNone(frontmatter, "SKILL.md needs YAML frontmatter")
        metadata = yaml.safe_load(frontmatter.group(1))
        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata["name"], "scientific-blender-animation")
        self.assertIsInstance(metadata["description"], str)
        self.assertTrue(metadata["description"].strip())
        self.assertLessEqual(len(metadata["description"]), 1024)
        if "compatibility" in metadata:
            self.assertIsInstance(metadata["compatibility"], str)
            self.assertTrue(0 < len(metadata["compatibility"]) <= 500)
        for key, value in metadata.get("metadata", {}).items():
            with self.subTest(metadata_key=key):
                self.assertIsInstance(key, str)
                self.assertIsInstance(value, str)

    def test_skill_local_markdown_links_resolve_inside_package(self):
        source = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        targets = re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", source)
        local_count = 0
        for target in targets:
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            local_count += 1
            with self.subTest(target=target):
                resolved = (ROOT / unquote(parsed.path)).resolve()
                self.assertTrue(resolved.is_relative_to(ROOT), "Link escapes the package")
                self.assertTrue(resolved.is_file(), "Local link target is missing")
        self.assertGreater(local_count, 0)

    def test_all_document_links_resolve_inside_package(self):
        """Catch broken relative paths across the platform guides and templates."""
        for document in ROOT.rglob("*.md"):
            if ".git" in document.parts:
                continue
            source = document.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", source):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                with self.subTest(document=str(document.relative_to(ROOT)), target=target):
                    resolved = (document.parent / unquote(parsed.path)).resolve()
                    self.assertTrue(resolved.is_relative_to(ROOT), "Link escapes the package")
                    self.assertTrue(resolved.exists(), "Local document link target is missing")


if __name__ == "__main__":
    unittest.main()
