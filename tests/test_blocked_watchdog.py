"""Tests for deterministic blocked watchdog."""

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WATCHDOG = REPO_ROOT / "skills" / "mochi-squad" / "scripts" / "blocked-watchdog.py"


def init_db(path: Path, blocked: bool = False):
    conn = sqlite3.connect(str(path))
    conn.execute("CREATE TABLE tasks (id TEXT PRIMARY KEY, title TEXT, assignee TEXT, status TEXT, updated_at INTEGER)")
    conn.execute("CREATE TABLE task_events (id INTEGER PRIMARY KEY, task_id TEXT, kind TEXT, created_at INTEGER, payload TEXT)")
    if blocked:
        conn.execute("INSERT INTO tasks VALUES ('t_1', 'Blocked task', 'mochi-exec', 'blocked', 2)")
        conn.execute("INSERT INTO task_events(task_id, kind, created_at, payload) VALUES ('t_1', 'blocked', 3, ?)", (json.dumps({"reason": "needs_context: missing input"}),))
    conn.commit()
    conn.close()


class TestBlockedWatchdog(unittest.TestCase):
    def test_quiet_when_no_blocked_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "kanban.db"
            state = Path(tmp) / "watch.json"
            init_db(db, blocked=False)
            result = subprocess.run([sys.executable, str(WATCHDOG), "--kanban-db", str(db), "--state-file", str(state)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")

    def test_new_blocked_event_outputs_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "kanban.db"
            state = Path(tmp) / "watch.json"
            init_db(db, blocked=True)
            first = subprocess.run([sys.executable, str(WATCHDOG), "--kanban-db", str(db), "--state-file", str(state)], capture_output=True, text=True, timeout=10)
            self.assertEqual(first.returncode, 0)
            self.assertIn("Mochi Squad blocked task detected", first.stdout)
            second = subprocess.run([sys.executable, str(WATCHDOG), "--kanban-db", str(db), "--state-file", str(state)], capture_output=True, text=True, timeout=10)
            self.assertEqual(second.returncode, 0)
            self.assertEqual(second.stdout, "")


if __name__ == "__main__":
    unittest.main()
