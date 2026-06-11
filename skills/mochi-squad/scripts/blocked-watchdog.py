#!/usr/bin/env python3
"""Mochi Squad blocked task watchdog.

Quiet watchdog pattern: stdout is empty when there are no new blocked events.
Use with Hermes cron no_agent=true so only non-empty output is delivered.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"seen": {}}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {"seen": {}, "warning": "state reset: invalid json"}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def latest_block_event(conn: sqlite3.Connection, task_id: str) -> tuple[str, str]:
    try:
        row = conn.execute(
            "SELECT id, created_at, payload FROM task_events WHERE task_id=? AND kind='blocked' ORDER BY created_at DESC, id DESC LIMIT 1",
            (task_id,),
        ).fetchone()
    except sqlite3.Error:
        return (f"task:{task_id}", "")
    if not row:
        return (f"task:{task_id}", "")
    event_id, created_at, payload = row
    reason = ""
    if payload:
        try:
            reason = json.loads(payload).get("reason", "")
        except Exception:
            reason = str(payload)[:300]
    return (f"event:{event_id}:{created_at}", reason)


def scan(db_path: Path, state_path: Path, dry_run: bool = False) -> str:
    if not db_path.exists():
        return ""
    state = load_state(state_path)
    seen = state.setdefault("seen", {})
    messages: list[str] = []
    with sqlite3.connect(str(db_path)) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, title, assignee, status FROM tasks WHERE status='blocked' ORDER BY updated_at DESC, id DESC"
        ).fetchall()
        for row in rows:
            key, reason = latest_block_event(conn, row["id"])
            dedupe_key = f"{row['id']}:{key}"
            if seen.get(dedupe_key):
                continue
            seen[dedupe_key] = True
            messages.append(
                "Mochi Squad blocked task detected\n"
                f"- task: {row['id']}\n"
                f"- title: {row['title']}\n"
                f"- assignee: {row['assignee']}\n"
                f"- reason: {reason or '(no blocked reason found)'}"
            )
    if messages and not dry_run:
        save_state(state_path, state)
    elif not messages and not dry_run and not state_path.exists():
        save_state(state_path, state)
    return "\n\n".join(messages)


def main() -> int:
    parser = argparse.ArgumentParser(description="Quiet blocked-task watchdog for Hermes Kanban")
    parser.add_argument("--kanban-db", default=os.environ.get("HERMES_KANBAN_DB", os.path.expanduser("~/.hermes/kanban.db")))
    parser.add_argument("--state-file", default=None, help="Dedupe state path (default: next to runtime state)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    db_path = Path(args.kanban_db).expanduser()
    state_path = Path(args.state_file).expanduser() if args.state_file else Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))) / "mochi-squad" / "blocked-watchdog-state.json"
    try:
        out = scan(db_path, state_path, dry_run=args.dry_run)
    except sqlite3.Error as exc:
        print(f"blocked-watchdog error: {exc}", file=sys.stderr)
        return 2
    if out:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
