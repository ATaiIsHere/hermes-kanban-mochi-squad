"""Tests for deterministic Mochi Squad setup."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP = REPO_ROOT / "skills" / "mochi-squad" / "scripts" / "setup.py"
CHECK = REPO_ROOT / "skills" / "mochi-squad" / "scripts" / "check_readiness.py"


def run_json(args):
    result = subprocess.run([sys.executable, str(SETUP), *args], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class TestSetupWorkflow(unittest.TestCase):
    def test_plan_is_side_effect_free(self):
        with tempfile.TemporaryDirectory() as home:
            out = run_json(["--hermes-home", home, "--plan"])
            self.assertEqual(out["action"], "plan")
            self.assertTrue(out["will_change"])
            self.assertFalse((Path(home) / "mochi-squad").exists())

    def test_install_creates_core_runtime_and_profiles(self):
        with tempfile.TemporaryDirectory() as home:
            out = run_json(["--hermes-home", home, "--install"])
            self.assertEqual(out["action"], "install")
            runtime = Path(home) / "mochi-squad"
            self.assertTrue((runtime / "config.yaml").exists())
            self.assertTrue((runtime / "state.yaml").exists())
            self.assertTrue((runtime / "scripts" / "blocked-watchdog.py").exists())
            for profile in ("mochi-exec", "mochi-review"):
                p = Path(home) / "profiles" / profile
                self.assertTrue((p / "SOUL.md").exists())
                self.assertTrue((p / "config.yaml").exists())
                self.assertTrue((p / "skills" / "mochi-squad" / "SKILL.md").exists())
            self.assertFalse((Path(home) / "profiles" / "mochi-plan").exists())
            state = json.loads((runtime / "state.yaml").read_text())
            self.assertIn("profiles", state)
            self.assertEqual(state["profiles"]["mochi-exec"]["status"], "ok")

    def test_install_is_idempotent(self):
        with tempfile.TemporaryDirectory() as home:
            run_json(["--hermes-home", home, "--install"])
            out = run_json(["--hermes-home", home, "--install"])
            self.assertTrue(out["skipped"])

    def test_verify_after_install_is_ready(self):
        with tempfile.TemporaryDirectory() as home:
            run_json(["--hermes-home", home, "--install"])
            out = run_json(["--hermes-home", home, "--verify"])
            self.assertEqual(out["action"], "verify")
            self.assertTrue(out["ready"])
            result = subprocess.run(
                [sys.executable, str(CHECK), "--hermes-home", home],
                capture_output=True, text=True, timeout=20,
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(json.loads(result.stdout)["ready"])

    def test_existing_profile_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as home:
            p = Path(home) / "profiles" / "mochi-exec"
            p.mkdir(parents=True)
            (p / "SOUL.md").write_text("custom soul\n")
            run_json(["--hermes-home", home, "--install"])
            self.assertEqual((p / "SOUL.md").read_text(), "custom soul\n")


if __name__ == "__main__":
    unittest.main()
