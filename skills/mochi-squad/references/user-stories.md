# Mochi Squad v0.1 User Stories and Acceptance Criteria

Status: v0.1 planning baseline.

## US-1 — Operator can safely install Mochi Squad runtime

As a Hermes operator, I want a deterministic setup flow so that the core runtime can be planned, installed, verified, and repaired without relying on LLM inference for every file operation.

Acceptance criteria:

- `setup.py --plan` reports intended changes without writing files.
- `setup.py --install` creates missing runtime directories, `config.yaml`, `state.yaml`, copied scripts, and core profiles without overwriting existing SOUL/config files.
- Core profiles are `mochi-exec` and `mochi-review`.
- Newly-created core profiles receive minimal SOUL templates and recommended Hermes-native profile config.
- Existing profiles are audited and reported; setup does not silently overwrite them.
- The `mochi-squad` skill is installed/synced into worker profile skill directories when missing.
- `check_readiness.py` is side-effect-free and reports `ok`/missing state for runtime files, profiles, skills, and watcher script.
- `state.yaml` records generated facts such as profile audit results and script checksums.
- Setup ships a deterministic blocked watcher script for no-agent cron usage; cron creation itself remains explicit/operator-approved.

## US-2 — Orchestrator can model a request as a Project

As an orchestrator, I want to represent a request as `root task + descendants` so that Project state can be derived from native Hermes Kanban without schema changes.

Acceptance criteria:

- Root task is the spec SSOT.
- Child tasks reference root/scenario IDs instead of copying the whole spec.
- Project lanes derive as PLANNING / IN_PROGRESS / BLOCKED / DONE from native task status and links.

## US-3 — Exec can implement and rerun safely

As `mochi-exec`, I want blocked attempts to record resume context so that reruns continue safely instead of blindly starting over.

Acceptance criteria:

- Exec block comments include completed, remaining, tried, artifacts/changed files, `do_not_repeat`, and `resume_hint`.
- Orchestrator can add `[resume-context]` and unblock the same exec task.

## US-4 — Review can verify without implementing fixes

As `mochi-review`, I want to run real verification and produce explicit verdicts without modifying implementation code.

Acceptance criteria:

- Review can use terminal for tests/builds/diffs/evidence.
- Verdicts include approve, needs_fix, block_human, and unsafe_to_continue.
- Review does not implement fixes.

## US-5 — Failed review inserts fix before the same review gate

As an orchestrator, I want review `needs_fix` to insert a scoped fix task before the same review task so that native dependencies rerun the gate after the fix.

Acceptance criteria:

- Review blocks with typed reason `needs_fix` and failed scenario evidence.
- Orchestrator links predecessor -> fix -> same review and unblocks review.
- Fix completion promotes/reruns the same review task.

## US-6 — PR handoff avoids active_pr guard traps

As a worker, I want PR handoff to use structured fields instead of raw retryable PR URLs so that Hermes respawn guard does not suppress retries.

Acceptance criteria:

- Retryable comments use `PR_REF`, `BRANCH`, `BASE`, `HEAD_SHA`, and `PR_POLICY`.
- Workers check for an existing PR before opening another.

## US-7 — Watcher runs deterministically and quietly

As an operator, I want blocked monitoring to be a deterministic script so quiet ticks cost no LLM calls and only new blocked events notify.

Acceptance criteria:

- `blocked-watchdog.py` emits no stdout when there is no new blocked event.
- New blocked events produce a concise notification payload.
- Dedupe state is stored in runtime state, not committed repo files.

## US-8 — Maintainers can verify package completeness

As a maintainer, I want tests to cover setup, templates, readiness, and watcher behavior so that future PRs do not omit agreed components.

Acceptance criteria:

- Tests verify core profile templates exist and are minimal.
- Tests verify setup plan/install/verify idempotency in a temporary Hermes home.
- Tests verify watcher quiet/new/dedupe behavior.
- Private/local term scan passes before publishing.
