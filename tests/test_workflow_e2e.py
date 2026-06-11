"""End-to-end convention test for review fix insertion."""

import unittest
from collections import defaultdict


class Graph:
    def __init__(self):
        self.status = {}
        self.children = defaultdict(list)

    def task(self, tid, status):
        self.status[tid] = status

    def link(self, parent, child):
        self.children[parent].append(child)

    def parents(self, child):
        return [p for p, cs in self.children.items() if child in cs]

    def ready(self, tid):
        return self.status[tid] in {"todo", "ready"} and all(self.status[p] == "done" for p in self.parents(tid))


def insert_fix_before_same_review(g: Graph, exec_id: str, review_id: str, fix_id: str):
    # Existing path root -> exec -> review. Add fix before same review gate.
    g.task(fix_id, "todo")
    g.link(exec_id, fix_id)
    g.link(fix_id, review_id)
    g.status[review_id] = "todo"


class TestReviewFixInsertionConvention(unittest.TestCase):
    def test_fix_blocks_same_review_until_done(self):
        g = Graph()
        g.task("root", "done")
        g.task("exec", "done")
        g.task("review", "blocked")
        g.link("root", "exec")
        g.link("exec", "review")

        insert_fix_before_same_review(g, "exec", "review", "fix")

        self.assertFalse(g.ready("review"))
        self.assertTrue(g.ready("fix"))
        g.status["fix"] = "done"
        self.assertTrue(g.ready("review"))


if __name__ == "__main__":
    unittest.main()
