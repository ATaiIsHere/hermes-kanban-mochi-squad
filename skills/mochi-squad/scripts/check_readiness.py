#!/usr/bin/env python3
"""Mochi Squad readiness checker — side-effect-free, cheap, JSON output.

Usage:
    python check_readiness.py [--runtime-dir PATH]

Checks:
    - Runtime state.json existence and version compatibility
    - Config file existence (template fallback)
    - Recorded profile existence (from state.json)
    - Virtual Office status

Returns JSON to stdout. Exits 0 on success (any readiness level),
non-zero on internal error.
"""

import argparse
import json
import os
import sys

SKILL_VERSION = "0.1.0"


def default_runtime_dir(hermes_home: str | None = None) -> str:
    """Return the default Mochi Squad runtime directory path."""
    base = hermes_home or os.environ.get("HERMES_HOME",
                                          os.path.expanduser("~/.hermes"))
    return os.path.join(base, "mochi", "mochi-squad")


def check_readiness(runtime_dir: str) -> dict:
    """Check runtime readiness without side effects."""
    result: dict = {
        "ready": False,
        "readiness": "skill_available",
        "skill_version": SKILL_VERSION,
        "setup_needed": False,
        "missing": [],
        "suggested_action": None,
    }

    state_path = os.path.join(runtime_dir, "state.json")
    config_path = os.path.join(runtime_dir, "config.yaml")

    # --- State file ---
    if os.path.isfile(state_path):
        try:
            with open(state_path) as f:
                state = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            result["missing"].append(f"state.json unreadable: {exc}")
            state = {}
        else:
            state_version = state.get("version")
            if state_version:
                result["state_version"] = state_version
                if state_version == SKILL_VERSION:
                    result["readiness"] = "runtime_ready"
                    result["ready"] = True
                else:
                    result["missing"].append(
                        f"state.json version {state_version} != "
                        f"skill {SKILL_VERSION}"
                    )
            else:
                result["missing"].append("state.json has no version field")
    else:
        result["readiness"] = "runtime_not_installed"
        result["setup_needed"] = True
        result["missing"].append("state.json not found")
        state = {}

    # --- Config file ---
    if os.path.isfile(config_path):
        result["config_exists"] = True
    else:
        result["config_exists"] = False
        entry = "config.yaml not found"
        if entry not in result["missing"]:
            result["missing"].append(entry)

    # --- Profiles (recorded in state) ---
    if state:
        recorded = state.get("profiles", {})
        found = sum(1 for v in recorded.values() if v.get("exists"))
        missing_profiles = sum(1 for v in recorded.values() if not v.get("exists"))
        result["profiles_checked"] = {"found": found, "missing": missing_profiles}

    # --- Virtual Office (from state) ---
    vo_enabled = False
    if state:
        vo = state.get("virtual_office", {})
        vo_enabled = vo.get("enabled", False)
    result["virtual_office"] = {
        "enabled": vo_enabled,
        "deferred": True,
    }

    # --- Suggested action ---
    if result["readiness"] == "runtime_not_installed":
        result["suggested_action"] = "run scripts/setup.py --install"
    elif not result["ready"]:
        result["suggested_action"] = (
            "run scripts/setup.py --verify --repair"
        )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Mochi Squad readiness checker")
    parser.add_argument(
        "--runtime-dir",
        default=None,
        help="Mochi Squad runtime directory path "
             "(default: $HERMES_HOME/mochi/mochi-squad)",
    )
    args = parser.parse_args()
    runtime_dir = args.runtime_dir or default_runtime_dir()
    result = check_readiness(runtime_dir)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())