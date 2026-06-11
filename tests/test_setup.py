"""Tests for deterministic Mochi Squad setup."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SETUP = REPO_ROOT / "scripts" / "setup.py"


def run_json(args):
    result = subprocess.run([sys.executable, str(SETUP), *args], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


class TestSetupWorkflow(unittest.TestCase):
    def test_plan_is_side_effect_free(self):
        with tempfile.TemporaryDirectory() as home:
            out = run_json(["--hermes-home", home, "--plan", "--install-cron"])
            self.assertEqual(out["action"], "plan")
            self.assertTrue(out["will_change"])
            self.assertFalse((Path(home) / "mochi-squad").exists())
            self.assertTrue(out["cron_install_requested"])

    def test_install_creates_core_runtime_profiles_and_cron(self):
        with tempfile.TemporaryDirectory() as home:
            out = run_json(["--hermes-home", home, "--install", "--install-cron"])
            self.assertEqual(out["action"], "install")
            runtime = Path(home) / "mochi-squad"
            self.assertTrue((runtime / "config.yaml").exists())
            self.assertTrue((runtime / "state.yaml").exists())
            self.assertTrue((runtime / "scripts" / "blocked-watchdog.py").exists())
            self.assertTrue((Path(home) / "scripts" / "mochi-squad-blocked-watchdog.py").exists())
            jobs = json.loads((Path(home) / "cron" / "jobs.json").read_text())
            self.assertEqual(jobs["jobs"][0]["no_agent"], True)
            self.assertEqual(jobs["jobs"][0]["script"], "mochi-squad-blocked-watchdog.py")
            for profile in ("mochi-exec", "mochi-review"):
                p = Path(home) / "profiles" / profile
                self.assertTrue((p / "SOUL.md").exists())
                self.assertTrue((p / "config.yaml").exists())
                self.assertTrue((p / "skills" / "mochi-squad" / "SKILL.md").exists())
            self.assertFalse((Path(home) / "profiles" / "mochi-plan").exists())
            self.assertFalse((Path(home) / "profiles" / "mochi-research").exists())
            state = json.loads((runtime / "state.yaml").read_text())
            self.assertTrue(state["blocked_watcher"]["cron_installed"])

    def test_review_profile_defaults_include_browser(self):
        with tempfile.TemporaryDirectory() as home:
            run_json(["--hermes-home", home, "--install"])
            cfg = (Path(home) / "profiles" / "mochi-review" / "config.yaml").read_text()
            self.assertIn("  - browser", cfg)
            self.assertIn("  - terminal", cfg)

    def test_existing_profile_is_not_overwritten_and_audit_proposes_diff(self):
        with tempfile.TemporaryDirectory() as home:
            p = Path(home) / "profiles" / "mochi-review"
            p.mkdir(parents=True)
            (p / "SOUL.md").write_text("custom soul with mochi-squad\n")
            (p / "config.yaml").write_text("skills:\n  - mochi-squad\nenabled_toolsets:\n  - file\n")
            run_json(["--hermes-home", home, "--install"])
            self.assertEqual((p / "SOUL.md").read_text(), "custom soul with mochi-squad\n")
            verify = run_json(["--hermes-home", home, "--verify"])
            audit = verify["profiles"]["mochi-review"]
            self.assertEqual(audit["status"], "warn")
            self.assertIn("missing_required_toolsets", audit["warnings"])
            self.assertIn("browser", audit["proposed_additions"]["enabled_toolsets"])

    def test_install_is_idempotent(self):
        with tempfile.TemporaryDirectory() as home:
            run_json(["--hermes-home", home, "--install", "--install-cron"])
            out = run_json(["--hermes-home", home, "--install", "--install-cron"])
            self.assertTrue(out["skipped"])
            jobs = json.loads((Path(home) / "cron" / "jobs.json").read_text())
            self.assertEqual(len(jobs["jobs"]), 1)


if __name__ == "__main__":
    unittest.main()
