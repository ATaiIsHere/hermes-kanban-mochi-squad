# PR Handoff Guard Policy

## Context

Hermes Kanban has a respawn guard that scans recent task comments for raw GitHub PR URLs. If a retryable task comment contains a URL such as `https://github.com/<owner>/<repo>/pull/<n>`, dispatcher may suppress respawn for roughly 24 hours with `respawn_guarded: active_pr`.

This is useful as a duplicate-PR heuristic, but it is broad: it does not distinguish exec/review task types and does not treat a later guard-safe comment as a replacement for an earlier raw URL. If the raw URL remains in recent comments, the guard can still fire until the window expires or an operator performs recovery.

## Rule

For any task that may be unblocked, reclaimed, retried, or re-run, do **not** put a raw GitHub PR URL in comments.

Use a structured handoff instead:

```text
PR_REF: owner/repo#123
BRANCH: feature/example
BASE: main
HEAD_SHA: <commit sha>
PR_POLICY: reuse_existing_pr=true; do_not_open_duplicate_pr=true
```

Workers must resolve `PR_REF` via GitHub tooling/API before acting. If an open PR already exists for the branch/head, update that PR rather than opening a duplicate.

## Where raw PR URLs are allowed

Raw PR URLs are acceptable only in surfaces that are not expected to trigger the same task's respawn path, such as:

- final user-facing report after the workflow is complete;
- downstream review task body when that downstream task is the intended next runnable unit;
- external release notes or repository documentation.

When in doubt, prefer `PR_REF` in Kanban comments.

## Already-triggered active_pr guard

A guard-safe follow-up comment does **not** cancel an earlier raw PR URL comment. If `active_pr` already fired because a raw URL exists in recent comments, choose one of:

1. wait for the guard window to expire;
2. create a continuation / re-review task that does not depend on retrying the guarded task;
3. perform explicit operator recovery, such as editing/removing the raw URL comment or applying an upstream guard fix.

Do not tell the user that adding `PR_REF` will unblock an already-guarded task by itself.

## Mochi Squad pattern

- Exec completion comments for code changes: use structured `PR_REF` handoff, not raw URLs.
- Review tasks: receive enough PR identity to find the PR, but must check for an existing PR before creating/updating anything.
- Review/fix loops: if guard has already trapped a retry path, prefer an explicit Mochi recovery path (operator recovery or a fresh continuation/re-review branch) over pretending the original blocked review completed. For normal review failure, use Review-Blocked Fix Insertion (`fix -> same review gate`) and avoid raw PR URLs in retryable comments.
