"""Tests for mochi-squad readiness checker."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts dir to path (resolve relative to this test file)
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "skills" / "mochi-squad" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_readiness import check_readiness, default_runtime_dir

# Allow running from repo root too
SCRIPTS_DIR_ALT = Path(__file__).resolve().parents[2] / "skills" / "mochi-squad" / "scripts"
if str(SCRIPTS_DIR_ALT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR_ALT))


class TestReadinessChecker(unittest.TestCase):
    """Test the side-effect-free readiness checker."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="mochi-test-")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_runtime_not_installed_when_state_missing(self):
        """When state.json is absent, readiness is runtime_not_installed."""
        result = check_readiness(self.tmpdir)
        self.assertFalse(result["ready"])
        self.assertEqual(result["readiness"], "runtime_not_installed")
        self.assertTrue(result["setup_needed"])
        self.assertIn("state.json not found", result["missing"])
        self.assertEqual(result["skill_version"], "0.1.0")

    def test_runtime_not_installed_when_config_missing(self):
        """Missing config.yaml is reported in missing list."""
        result = check_readiness(self.tmpdir)
        self.assertFalse(result.get("config_exists", True))

    def test_readiness_ready_with_valid_state(self):
        """When state.json exists with matching version, readiness is runtime_ready."""
        state_path = os.path.join(self.tmpdir, "state.json")
        with open(state_path, "w") as f:
            json.dump({"version": "0.1.0"}, f)
        config_path = os.path.join(self.tmpdir, "config.yaml")
        with open(config_path, "w") as f:
            f.write("profiles:\n  exec: mochi-exec\n")

        result = check_readiness(self.tmpdir)
        self.assertTrue(result["ready"])
        self.assertEqual(result["readiness"], "runtime_ready")
        self.assertEqual(result["state_version"], "0.1.0")

    def test_version_mismatch_reported(self):
        """When state version differs, readiness is skill_available (not ready)."""
        state_path = os.path.join(self.tmpdir, "state.json")
        with open(state_path, "w") as f:
            json.dump({"version": "0.2.0"}, f)

        result = check_readiness(self.tmpdir)
        self.assertFalse(result["ready"])
        self.assertIn("0.2.0", result["missing"][0] if result["missing"] else "")
        self.assertIn("!=", result["missing"][0] if result["missing"] else "")

    def test_default_runtime_dir_from_env(self):
        """default_runtime_dir uses HERMES_HOME env var."""
        os.environ["HERMES_HOME"] = "/custom/hermes"
        try:
            path = default_runtime_dir()
            self.assertTrue(path.endswith("/mochi/mochi-squad"))
            self.assertIn("/custom/hermes", path)
        finally:
            os.environ.pop("HERMES_HOME", None)

    def test_default_runtime_dir_fallback(self):
        """default_runtime_dir falls back to ~/.hermes when env is unset."""
        os.environ.pop("HERMES_HOME", None)
        path = default_runtime_dir()
        self.assertTrue(path.endswith("/mochi/mochi-squad"))
        self.assertIn(".hermes", path)

    def test_side_effect_free(self):
        """check_readiness must not create files."""
        before = set(os.listdir(self.tmpdir))
        check_readiness(self.tmpdir)
        after = set(os.listdir(self.tmpdir))
        self.assertEqual(before, after)

    def test_profiles_from_state(self):
        """profiles_checked is populated from state.json."""
        state_path = os.path.join(self.tmpdir, "state.json")
        with open(state_path, "w") as f:
            json.dump({
                "version": "0.1.0",
                "profiles": {
                    "mochi-exec": {"exists": True},
                    "mochi-review": {"exists": True},
                    "mochi-plan": {"exists": False},
                },
            }, f)

        result = check_readiness(self.tmpdir)
        self.assertIn("profiles_checked", result)
        self.assertEqual(result["profiles_checked"]["found"], 2)
        self.assertEqual(result["profiles_checked"]["missing"], 1)

    def test_virtual_office_deferred(self):
        """Virtual Office shows as deferred."""
        result = check_readiness(self.tmpdir)
        self.assertIn("virtual_office", result)
        self.assertTrue(result["virtual_office"]["deferred"])

    def test_suggested_action_on_missing_runtime(self):
        """When runtime is not installed, suggested action points to setup."""
        result = check_readiness(self.tmpdir)
        self.assertIsNotNone(result["suggested_action"])
        self.assertIn("setup.py", result["suggested_action"])


class TestReadinessMain(unittest.TestCase):
    """Test check_readiness.py CLI entry point."""

    def test_cli_json_output(self):
        """Running check_readiness against nonexistent dir yields valid JSON."""
        import subprocess
        script = SCRIPTS_DIR / "check_readiness.py"
        result = subprocess.run(
            [sys.executable, str(script), "--runtime-dir", "/tmp/mochi-nonexistent-test-0000"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("readiness", data)
        self.assertIn("missing", data)


if __name__ == "__main__":
    unittest.main()