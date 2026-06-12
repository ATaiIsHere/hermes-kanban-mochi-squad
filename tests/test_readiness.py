"""Tests for side-effect-free readiness checker."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from check_readiness import check_readiness


class TestReadinessChecker(unittest.TestCase):
    def setUp(self):
        self.home = tempfile.mkdtemp(prefix="mochi-home-")
        self.runtime = str(Path(self.home) / "mochi-squad")

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)

    def test_missing_runtime_reports_not_installed(self):
        result = check_readiness(self.runtime, hermes_home=self.home)
        self.assertFalse(result["ready"])
        self.assertEqual(result["readiness"], "runtime_not_installed")
        self.assertIn("runtime_dir", result["missing"])

    def test_side_effect_free(self):
        before = set(Path(self.home).iterdir())
        check_readiness(self.runtime, hermes_home=self.home)
        after = set(Path(self.home).iterdir())
        self.assertEqual(before, after)

    def test_ready_after_setup_install(self):
        subprocess.run([sys.executable, str(SCRIPTS_DIR / "setup.py"), "--hermes-home", self.home, "--install", "--install-cron"], check=True, capture_output=True, text=True)
        result = check_readiness(self.runtime, hermes_home=self.home)
        self.assertTrue(result["ready"])
        self.assertEqual(result["readiness"], "runtime_ready")
        self.assertEqual(result["skill_version"], "0.2.0")
        self.assertIsNotNone(result["cron"])

    def test_cli_json_output(self):
        result = subprocess.run([sys.executable, str(SCRIPTS_DIR / "check_readiness.py"), "--hermes-home", self.home], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0)
        self.assertIn("readiness", json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
