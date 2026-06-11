# Orchestrator Guideline

Use this role when turning user intent into a durable Kanban Project and routing work to specialists.

## Required Shared References

- `references/shared/project-graph-conventions.md`
- `references/shared/review-fix-loop.md` when handling blocked exec/review tasks
- `references/shared/pr-handoff-guard-policy.md` when a PR is involved
- `references/setup-readiness.md` when installing or verifying Mochi runtime

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

## Handoff Quality

Child task bodies should reference root task/scenario IDs and name exact deliverables. They should not copy the entire root spec.

Each task should define:

- role and boundaries;
- inputs and target scenarios;
- deliverables;
- verification expected before handoff;
- how to block if needed.
