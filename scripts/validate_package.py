#!/usr/bin/env python3
"""Validate Mochi Squad package layout and public-safety invariants."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "references/change-spec-format.md",
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
    "templates/profiles/mochi-exec/SOUL.md",
    "templates/profiles/mochi-review/SOUL.md",
    "scripts/setup.py",
    "scripts/check_readiness.py",
    "scripts/blocked-watchdog.py",
]
ROUTED = [
    "references/change-spec-format.md",
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
PRIVATE_PATTERNS = [
    "/" + "opt" + "/" + "data",
    "atai" + r"\.dev",
    "discord" + r":\d",
    "telegram" + r":\d",
    "a710" + "4710",
    "BEGIN " + r"(RSA |OPENSSH |EC )?" + "PRIVATE" + " KEY",
]
ALLOW_PRIVATE_IN = {"references/open-source-packaging.md"}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def main() -> int:
    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            fail(f"missing required file: {rel}")
    if (ROOT / "skills").exists():
        fail("single-skill repo must not contain nested skills/ directory")
    if (ROOT / "templates/profiles/mochi-plan").exists():
        fail("core package must not include mochi-plan profile template")
    if (ROOT / "templates/profiles/mochi-research").exists():
        fail("core package must not include mochi-research profile template")
    skill = (ROOT / "SKILL.md").read_text()
    for rel in ROUTED:
        if rel not in skill:
            fail(f"SKILL.md does not route {rel}")
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in {".git", "__pycache__"} for part in path.parts):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOW_PRIVATE_IN:
            continue
        if path.suffix in {".pyc", ".db", ".sqlite", ".pem", ".key"}:
            fail(f"forbidden generated/secret-like file committed: {rel}")
        text = path.read_text(errors="ignore")
        for pat in PRIVATE_PATTERNS:
            if re.search(pat, text, re.IGNORECASE):
                fail(f"private/local pattern {pat!r} found in {rel}")
    print("package validation ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
