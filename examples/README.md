# Workflow examples

These examples show how to model Mochi Squad-style project workflows on top of native Hermes Kanban.

Core convention:

```text
Project = one root/spec task + all descendant tasks linked from it
```

The examples intentionally use only native Kanban concepts: task body, task status, parent/child dependencies, comments, run summaries, and run metadata. They do not require custom database fields, a daemon, a server, or Virtual Office APIs.

Examples:

- `basic-linear-workflow.md` — root/spec -> exec -> review.
- `block-rerun-and-fix-insertion.md` — current normal recovery path: exec rerun in place and review fix insertion before the same review gate.
- `review-fix-re-review.md` — legacy/exceptional pattern where a failed review stays blocked and work continues through a separate fix/re-review branch.
- `resolve-block-flow.md` — legacy/exceptional pattern where blocked execution stays blocked, then resolve-block -> replacement execution -> review.

Use these files as copyable patterns when writing README sections, skill references, or task bodies.