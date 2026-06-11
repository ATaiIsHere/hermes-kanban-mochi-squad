# Mochi Squad v0.1 User Stories and Acceptance Criteria

## US-1 — Operator can safely install Mochi Squad runtime

As a Hermes operator, I want deterministic setup scripts so core runtime/profile/watcher setup can be planned, installed, verified, and repaired without relying on LLM inference for every file operation.

Acceptance criteria:

- `setup.py --plan` reports intended changes without writing files.
- `setup.py --install` creates missing runtime directories, `config.yaml`, `state.yaml`, copied scripts, and core profiles without overwriting existing SOUL/config files.
- Core profiles are `mochi-exec` and `mochi-review`.
- `mochi-research` is optional/future and not installed by core setup.
- Newly-created core profiles receive minimal SOUL templates and recommended Hermes-native profile config.
- Existing profiles are audited and produce proposed additions instead of silent edits.
- `check_readiness.py` is side-effect-free.
- `state.yaml` records generated facts such as profile audit results, script checksums, and cron job IDs.
- Blocked watcher logic is deterministic and suitable for no-agent cron.

## US-2 — Orchestrator can model a request as a Project

Project = root task + descendants, with state derived from native Kanban task status and links.

## US-3 — Exec can implement and rerun safely

Exec blocks include resume context so the same task can rerun when scope remains correct.

## US-4 — Review can verify without implementing fixes

Review runs real checks and returns `approve`, `needs_fix`, `block_human`, or `unsafe_to_continue` without modifying implementation code.

## US-5 — Failed review inserts fix before the same review gate

`needs_fix` creates a scoped fix dependency before the same review task, then review reruns after fix completion.

## US-6 — PR handoff avoids active PR guard traps

Retryable PR handoffs use `PR_REF`, `BRANCH`, `BASE`, `HEAD_SHA`, and `PR_POLICY`.

## US-7 — Watcher runs deterministically and quietly

No new blocked event means empty stdout. New events produce one concise notification and update local dedupe state.

## US-8 — Maintainers can verify package completeness

Tests cover layout, routing, setup idempotency, profile audit, watcher behavior, workflow conventions, and private/local term safety.
