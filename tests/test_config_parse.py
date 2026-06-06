"""Tests for mochi-squad config/template parsing."""

import json
import os
import sys
import yaml
import tempfile
import unittest
from pathlib import Path

# Project root
REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = REPO_ROOT / "skills" / "mochi-squad" / "templates"


class TestConfigTemplateParsing(unittest.TestCase):
    """Validate mochi-squad.config.yaml template is valid YAML and has expected structure."""

    @classmethod
    def setUpClass(cls):
        cls.config_path = TEMPLATES_DIR / "mochi-squad.config.yaml"

    def test_template_exists(self):
        self.assertTrue(
            self.config_path.exists(),
            f"Config template not found at {self.config_path}",
        )

    def test_template_is_valid_yaml(self):
        with open(self.config_path) as f:
            try:
                data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                self.fail(f"Invalid YAML: {e}")
        self.assertIsNotNone(data, "YAML parsed to None")

    def test_template_has_profiles(self):
        with open(self.config_path) as f:
            data = yaml.safe_load(f)
        self.assertIn("profiles", data)
        profiles = data["profiles"]
        for key in ("plan", "exec", "review"):
            self.assertIn(key, profiles, f"Missing profile key: {key}")
            self.assertIsInstance(profiles[key], str)

    def test_template_has_watchers(self):
        with open(self.config_path) as f:
            data = yaml.safe_load(f)
        self.assertIn("watchers", data)
        self.assertIn("blocked", data["watchers"])
        blocked = data["watchers"]["blocked"]
        self.assertIn("enabled", blocked)
        self.assertFalse(blocked["enabled"])

    def test_template_virtual_office_disabled(self):
        with open(self.config_path) as f:
            data = yaml.safe_load(f)
        self.assertIn("virtual_office", data)
        self.assertFalse(data["virtual_office"]["enabled"])


class TestReadinessOutputShape(unittest.TestCase):
    """Validate that check_readiness.py produces correct JSON shape."""

    def test_json_output_shape(self):
        """Readiness JSON has expected top-level keys."""
        SCRIPTS_DIR = REPO_ROOT / "skills" / "mochi-squad" / "scripts"
        sys.path.insert(0, str(SCRIPTS_DIR))
        from check_readiness import check_readiness

        with tempfile.TemporaryDirectory() as tmp:
            result = check_readiness(tmp)

        required_keys = {
            "ready", "readiness", "skill_version",
            "setup_needed", "missing", "suggested_action",
        }
        self.assertTrue(
            required_keys.issubset(result.keys()),
            f"Missing keys: {required_keys - result.keys()}",
        )


if __name__ == "__main__":
    unittest.main()