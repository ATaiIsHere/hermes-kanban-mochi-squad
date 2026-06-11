"""Tests for mochi-squad readiness checker."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "skills" / "mochi-squad" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_readiness import check_readiness, default_runtime_dir


class TestReadinessChecker(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="mochi-home-")
        self.runtime = os.path.join(self.home, "mochi-squad")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_runtime_not_installed_when_state_missing(self):
        result = check_readiness(self.runtime, hermes_home=self.home)
        self.assertFalse(result["ready"])
        self.assertEqual(result["readiness"], "runtime_not_installed")
        self.assertTrue(result["setup_needed"])
        self.assertIn("state_yaml", result["missing"])
        self.assertEqual(result["skill_version"], "0.1.0")

    def test_side_effect_free(self):
        before = set(os.listdir(self.home))
        check_readiness(self.runtime, hermes_home=self.home)
        after = set(os.listdir(self.home))
        self.assertEqual(before, after)

    def test_default_runtime_dir_from_env(self):
        os.environ["HERMES_HOME"] = "/custom/hermes"
        try:
            path = default_runtime_dir()
            self.assertTrue(path.endswith("/mochi-squad"))
            self.assertIn("/custom/hermes", path)
        finally:
            os.environ.pop("HERMES_HOME", None)

    def test_readiness_ready_after_minimal_install_shape(self):
        runtime = Path(self.runtime)
        runtime.mkdir(parents=True)
        (runtime / "config.yaml").write_text("profiles:\n  exec: mochi-exec\n  review: mochi-review\n")
        (runtime / "state.yaml").write_text(json.dumps({"version": "0.1.0", "virtual_office": {"enabled": False}}))
        (runtime / "scripts").mkdir()
        (runtime / "scripts" / "blocked-watchdog.py").write_text("# placeholder\n")
        for name in ("mochi-exec", "mochi-review"):
            p = Path(self.home) / "profiles" / name
            (p / "skills" / "mochi-squad").mkdir(parents=True)
            (p / "SOUL.md").write_text("load mochi-squad\n")
            (p / "config.yaml").write_text("skills:\n  - mochi-squad\n")
        result = check_readiness(self.runtime, hermes_home=self.home)
        self.assertTrue(result["ready"])
        self.assertEqual(result["readiness"], "runtime_ready")

    def test_version_mismatch_reported(self):
        runtime = Path(self.runtime)
        runtime.mkdir(parents=True)
        (runtime / "state.yaml").write_text(json.dumps({"version": "0.2.0"}))
        result = check_readiness(self.runtime, hermes_home=self.home)
        self.assertFalse(result["ready"])
        self.assertTrue(any("state.version" in item for item in result["missing"]))

    def test_cli_json_output(self):
        import subprocess
        script = SCRIPTS_DIR / "check_readiness.py"
        result = subprocess.run(
            [sys.executable, str(script), "--hermes-home", self.home, "--runtime-dir", self.runtime],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("readiness", data)
        self.assertIn("missing", data)


if __name__ == "__main__":
    unittest.main()
