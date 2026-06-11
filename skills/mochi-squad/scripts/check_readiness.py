#!/usr/bin/env python3
"""Mochi Squad readiness checker — side-effect-free JSON output."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

SKILL_VERSION = "0.1.0"
CORE_PROFILES = ("mochi-exec", "mochi-review")


def default_runtime_dir(hermes_home: str | None = None) -> str:
    base = hermes_home or os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    return str(Path(base).expanduser() / "mochi-squad")


def read_json_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        return {"_parse_error": str(exc)}


def check_readiness(runtime_dir: str, hermes_home: str | None = None) -> dict[str, Any]:
    runtime = Path(runtime_dir).expanduser()
    home = Path(hermes_home or os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))).expanduser()
    state_path = runtime / "state.yaml"
    config_path = runtime / "config.yaml"
    state = read_json_yaml(state_path)

    checks = {
        "runtime_dir": runtime.is_dir(),
        "config_yaml": config_path.is_file(),
        "state_yaml": state_path.is_file() and not state.get("_parse_error"),
        "watchdog_script": (runtime / "scripts" / "blocked-watchdog.py").is_file(),
    }
    profiles: dict[str, Any] = {}
    for name in CORE_PROFILES:
        pdir = home / "profiles" / name
        profiles[name] = {
            "exists": pdir.is_dir(),
            "soul_exists": (pdir / "SOUL.md").is_file(),
            "config_exists": (pdir / "config.yaml").is_file(),
            "skill_installed": (pdir / "skills" / "mochi-squad").is_dir(),
        }

    missing = [name for name, ok in checks.items() if not ok]
    for name, data in profiles.items():
        for key, ok in data.items():
            if not ok:
                missing.append(f"profiles.{name}.{key}")

    version = state.get("version") if state else None
    if state and version != SKILL_VERSION:
        missing.append(f"state.version {version!r} != {SKILL_VERSION!r}")

    ready = not missing
    readiness = "runtime_ready" if ready else "runtime_not_installed"
    if not ready and state_path.exists() and config_path.exists():
        readiness = "runtime_warn"

    return {
        "ready": ready,
        "readiness": readiness,
        "skill_version": SKILL_VERSION,
        "state_version": version,
        "setup_needed": not ready,
        "runtime_dir": str(runtime),
        "hermes_home": str(home),
        "checks": checks,
        "profiles_checked": profiles,
        "missing": missing,
        "virtual_office": {"enabled": bool(state.get("virtual_office", {}).get("enabled", False)) if state else False, "deferred": True},
        "suggested_action": None if ready else "run scripts/setup.py --plan, then scripts/setup.py --install or --repair",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Mochi Squad readiness checker")
    parser.add_argument("--runtime-dir", default=None)
    parser.add_argument("--hermes-home", default=None)
    args = parser.parse_args()
    home = args.hermes_home or os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    runtime_dir = args.runtime_dir or default_runtime_dir(home)
    json.dump(check_readiness(runtime_dir, hermes_home=home), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
