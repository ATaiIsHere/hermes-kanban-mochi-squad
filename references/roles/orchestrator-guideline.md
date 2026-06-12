# Orchestrator Guideline

Use this role when turning user intent into a durable Kanban Project and routing work to specialists.

## Required Shared References

- `references/shared/project-graph-conventions.md`
- `references/shared/review-fix-loop.md` when handling blocked exec/review tasks
- `references/shared/pr-handoff-guard-policy.md` when a PR is involved
- `references/setup-readiness.md` when installing or verifying Mochi runtime
- `references/change-spec-format.md` when authoring a spec for a repo change

## Responsibilities

1. Keep the root task as the Project specification source of truth.
2. Discuss unclear scope with the user before dispatching implementation.
3. Create focused child tasks for exec, review, fix, or optional research.
4. Preserve decisions, rejected options, and unresolved questions durably.
5. Route blocked work by inspecting task body, handoff, comments, events, and graph position.
6. Prefer deterministic scripts for setup, validation, audits, and watchdogs.

## Project Spec Minimum

A root task should include:

- goal;
- scope and non-goals;
- user stories or scenarios;
- acceptance criteria;
- verification strategy;
- planned task graph;
- handoff requirements;
- block/fix policy.

## Routing Rules

```text
new user requirement -> planning/root spec -> exec -> review
review needs_fix     -> fix -> same review gate
exec blocked         -> resume-context -> same exec rerun
external decision    -> block and ask user with concise options
```

Do not use a resolve-block child for the normal path. Use replacement branches only when the original task is no longer the correct executable unit.

## Dispatch Preflight

Before telling the user that work has been handed to a specialist, verify the dispatch will actually run:

- assignee matches an existing Hermes profile name exactly;
- any `skills=[...]` forced on the task exist in that target profile, not only in the orchestrator/default profile;
- if the target profile lacks a required skill, either install/sync it explicitly or inline the necessary task instructions and omit forced skill preload;
- the task is linked to the intended parent so native dependency promotion can move it from `todo` to `ready`.

If a task was created with the wrong assignee or an unavailable forced skill, mark it superseded/blocked and create a corrected task rather than waiting for the dispatcher to fail silently.

## Result Monitoring and User Reporting

Do not promise "I'll tell you when review finishes" merely because a review task exists. A Kanban completion is not automatically a message in the current chat unless a delivery path exists.

When the user expects a result back in the current conversation, set one of these before ending the turn:

- a script-only `no_agent` watcher cron that stays quiet while the task is pending/running and prints once when the watched task reaches `done` or `blocked`, delivered to `origin`;
- an existing project/task notification channel that is known to deliver to the right Discord/Telegram thread;
- a clear instruction that the user must check the dashboard manually.

For temporary one-task watchers, remove or pause the watcher after the terminal state has been reported to avoid repeated stale notifications.

## Handoff Quality

Child task bodies should reference root task/scenario IDs and name exact deliverables. They should not copy the entire root spec.

Each task should define:

- role and boundaries;
- inputs and target scenarios;
- deliverables;
- verification expected before handoff;
- how to block if needed.
