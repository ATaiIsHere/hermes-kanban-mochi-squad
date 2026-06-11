"""Tests for Mochi Squad package layout and routing."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestPackageLayout(unittest.TestCase):
    def test_single_skill_root_layout(self):
        self.assertTrue((REPO_ROOT / "SKILL.md").exists())
        self.assertFalse((REPO_ROOT / "skills").exists())
        for directory in ("references", "templates", "scripts", "examples", "tests"):
            self.assertTrue((REPO_ROOT / directory).is_dir(), directory)

    def test_role_and_shared_references_exist(self):
        required = [
            "references/roles/orchestrator-guideline.md",
            "references/roles/exec-guideline.md",
            "references/roles/review-guideline.md",
            "references/roles/researcher-guideline.md",
            "references/shared/project-graph-conventions.md",
            "references/shared/review-fix-loop.md",
            "references/shared/pr-handoff-guard-policy.md",
            "references/setup-readiness.md",
            "references/open-source-packaging.md",
            "references/user-stories.md",
        ]
        for rel in required:
            self.assertTrue((REPO_ROOT / rel).is_file(), rel)

    def test_skill_routes_every_active_reference(self):
        skill = (REPO_ROOT / "SKILL.md").read_text()
        routed = [
            "references/roles/orchestrator-guideline.md",
            "references/roles/exec-guideline.md",
            "references/roles/review-guideline.md",
            "references/roles/researcher-guideline.md",
            "references/shared/project-graph-conventions.md",
            "references/shared/review-fix-loop.md",
            "references/shared/pr-handoff-guard-policy.md",
            "references/setup-readiness.md",
            "references/open-source-packaging.md",
            "references/user-stories.md",
        ]
        for rel in routed:
            self.assertIn(rel, skill)

    def test_config_template_has_runtime_sections_without_profile_mapping(self):
        text = (REPO_ROOT / "templates" / "mochi-squad.config.yaml").read_text()
        self.assertIn("kanban:", text)
        self.assertIn("watchers:", text)
        self.assertIn("virtual_office:", text)
        self.assertNotIn("research: mochi-research", text)
        self.assertNotIn("plan: mochi-plan", text)

    def test_profile_templates_core_only(self):
        profiles_dir = REPO_ROOT / "templates" / "profiles"
        self.assertTrue((profiles_dir / "mochi-exec" / "SOUL.md").is_file())
        self.assertTrue((profiles_dir / "mochi-review" / "SOUL.md").is_file())
        self.assertFalse((profiles_dir / "mochi-plan").exists())
        self.assertFalse((profiles_dir / "mochi-research").exists())

    def test_core_templates_are_minimal_and_route_to_role_guides(self):
        expectations = {
            "mochi-exec": "references/roles/exec-guideline.md",
            "mochi-review": "references/roles/review-guideline.md",
        }
        for profile, guide in expectations.items():
            text = (REPO_ROOT / "templates" / "profiles" / profile / "SOUL.md").read_text()
            self.assertIn("mochi-squad", text)
            self.assertIn(guide, text)
            self.assertLessEqual(len(text.splitlines()), 30)


if __name__ == "__main__":
    unittest.main()
