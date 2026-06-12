#!/usr/bin/env python3
"""Side-effect-free Mochi Squad readiness checker."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from setup import SKILL_VERSION, default_hermes_home, default_runtime_dir, verify


def check_readiness(runtime_dir: str | None = None, hermes_home: str | None = None) -> dict:
    home = default_hermes_home(hermes_home)
    runtime = Path(runtime_dir).expanduser().resolve() if runtime_dir else default_runtime_dir(home)
    result = verify(home, runtime)
    actionable_missing = []
    for check in result["checks"]:
        if not check["ok"] and check.get("severity") in {"fail", "warn"}:
            actionable_missing.append(check["name"])
    return {
        "ready": result["ready"] and result["readiness"] == "runtime_ready",
        "readiness": result["readiness"],
        "skill_version": SKILL_VERSION,
        "setup_needed": bool(actionable_missing),
        "runtime_dir": str(runtime),
        "hermes_home": str(home),
        "missing": actionable_missing,
        "checks": result["checks"],
        "profiles_checked": result["profiles"],
        "cron": result["cron"],
        "suggested_action": result["suggested_action"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Mochi Squad readiness checker")
    parser.add_argument("--runtime-dir", default=None)
    parser.add_argument("--hermes-home", default=None)
    args = parser.parse_args()
    json.dump(check_readiness(args.runtime_dir, args.hermes_home), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
