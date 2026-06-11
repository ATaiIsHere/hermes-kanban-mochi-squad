"""Tests for mochi-squad config/template parsing."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO_ROOT / "skills" / "mochi-squad" / "templates"


class TestConfigTemplateParsing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_path = TEMPLATES_DIR / "mochi-squad.config.yaml"

    def test_template_exists(self):
        self.assertTrue(self.config_path.exists())

    def test_template_is_valid_yaml(self):
        data = yaml.safe_load(self.config_path.read_text())
        self.assertIsNotNone(data)

    def test_template_has_core_profiles(self):
        data = yaml.safe_load(self.config_path.read_text())
        profiles = data["profiles"]
        self.assertEqual(profiles["exec"], "mochi-exec")
        self.assertEqual(profiles["review"], "mochi-review")
        self.assertNotIn("plan", profiles)

    def test_template_has_runtime_sections(self):
        data = yaml.safe_load(self.config_path.read_text())
        self.assertIn("kanban", data)
        self.assertIn("watchers", data)
        self.assertIn("virtual_office", data)
        self.assertFalse(data["watchers"]["blocked"]["enabled"])
        self.assertFalse(data["virtual_office"]["enabled"])


class TestProfileTemplates(unittest.TestCase):
    def test_profile_templates_exist(self):
        profiles_dir = TEMPLATES_DIR / "profiles"
        self.assertTrue((profiles_dir / "README.md").exists())
        for name in ("mochi-exec", "mochi-review", "mochi-research"):
            self.assertTrue((profiles_dir / name / "SOUL.md").exists(), name)
        self.assertFalse((profiles_dir / "mochi-plan" / "SOUL.md").exists())

    def test_core_templates_route_to_mochi_squad(self):
        profiles_dir = TEMPLATES_DIR / "profiles"
        for name in ("mochi-exec", "mochi-review"):
            text = (profiles_dir / name / "SOUL.md").read_text()
            self.assertIn("mochi-squad", text)
            self.assertIn("Required guidance", text)

    def test_templates_are_minimal(self):
        profiles_dir = TEMPLATES_DIR / "profiles"
        for name in ("mochi-exec", "mochi-review", "mochi-research"):
            text = (profiles_dir / name / "SOUL.md").read_text()
            self.assertLessEqual(len(text.splitlines()), 45)


class TestReadinessOutputShape(unittest.TestCase):
    def test_json_output_shape(self):
        scripts_dir = REPO_ROOT / "skills" / "mochi-squad" / "scripts"
        sys.path.insert(0, str(scripts_dir))
        from check_readiness import check_readiness
        with tempfile.TemporaryDirectory() as tmp:
            result = check_readiness(str(Path(tmp) / "mochi-squad"), hermes_home=tmp)
        required = {"ready", "readiness", "skill_version", "setup_needed", "missing", "suggested_action"}
        self.assertTrue(required.issubset(result.keys()))


if __name__ == "__main__":
    unittest.main()
