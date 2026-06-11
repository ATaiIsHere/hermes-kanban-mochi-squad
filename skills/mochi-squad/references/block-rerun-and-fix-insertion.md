# Block / Rerun / Fix Insertion

Status: current Mochi Squad v0.1 workflow consensus.

This reference defines how Mochi Squad handles blocked exec/review tasks without adding resolve-block tasks in the normal path. Native Hermes Kanban remains unchanged: project structure is still a root task plus descendants, task links are dependencies, comments/runs are the audit timeline, and `blocked` is a native task status.

## Core Rule

Use the original task whenever it is still the right executable unit.

```text
exec block   -> supplement/resume-context -> unblock same exec -> rerun
review block -> insert fix before review   -> unblock same review -> fix done reruns review
```

Do not create resolve-block tasks for the normal path. Historical detail belongs in task comments and run records; the task graph should express the current executable dependency path.

Only notify the user when the orchestrator decides the issue needs a human-owned decision: product behavior, scope, UX preference, credentials/permissions, cost, risk, or unsafe side effects.

## Typed Block Reasons

Workers should make block reasons machine-routeable. Use a short type at the start of the block reason, then a human summary.

```text
needs_context: missing detail that the orchestrator may be able to supply
needs_env: environment, dependency, service, credential, or permission problem
needs_fix: review found clear fixable failed scenarios
needs_orchestrator_triage: worker cannot safely decide the next step
needs_user_decision: user-owned product/scope/UX/risk/cost decision required
unsafe_to_continue: continuing may damage data, services, or external state
```

Routing defaults:

- `needs_context`, `needs_env`, `needs_orchestrator_triage`: Mochi/orchestrator triages first; do not notify the user by default.
- `needs_fix` on review: use Review-Blocked Fix Insertion.
- `needs_user_decision` or `unsafe_to_continue`: notify/block for user input unless the operator already supplied the decision.

## Exec Block Rerun

Exec blocks usually mean the worker needs more context, environment recovery, a narrower instruction, or an orchestrator decision. The default is to unblock and rerun the same exec task after adding a resume comment.

Flow:

```text
root -> exec(blocked)
Mochi reads task body, parent handoff, run summary/metadata, comments, block reason, and workspace evidence
Mochi adds [resume-context] comment or updates root spec if the effective requirements changed
Mochi unblocks exec
exec reruns and continues from recorded progress
exec done -> downstream tasks dispatch
```

A rerun is not necessarily from scratch. The blocked exec must record what was already completed, what remains, and what must not be repeated or overwritten.

Minimum exec block comment shape:

```text
[exec-block]
attempt: <n>
reason_type: needs_context | needs_env | needs_orchestrator_triage | needs_user_decision | unsafe_to_continue
completed:
- ...
remaining:
- ...
tried:
- ...
artifacts_or_changed_files:
- ...
do_not_repeat:
- ...
resume_hint:
- ...
needs_from_mochi_or_user:
- ...
```

Mochi resume comment shape:

```text
[resume-context]
for_task: <task-id>
for_attempt: <n+1>
decision_or_context:
- ...
continue_from:
- ...
do_not_repeat:
- ...
next_steps:
- ...
root_spec_updated: yes | no
```

If the original exec task is no longer the right work item, stop and replan. Do not pretend the blocked exec succeeded. The orchestrator should update the root spec, explain the supersession in comments, and create a replacement branch only after deciding how to keep downstream dependencies honest.

## Review-Blocked Fix Insertion

The review task is the gate. If review finds clear fixable issues, it blocks with `needs_fix` and records failed scenarios/evidence. Mochi inserts a fix task before the same review task, then unblocks review so native dependency gating reruns it after the fix completes.

Initial graph:

```text
root -> exec -> review
```

Review finds fixable problems:

```text
root -> exec -> review(blocked: needs_fix)
```

Mochi inserts fix before review:

```text
root -> exec -> fix -> review(unblocked, waiting on fix)
fix done -> review auto-promotes/reruns
```

Operation order:

1. Review blocks with `needs_fix` and comments failed scenarios/evidence.
2. Mochi creates a fix task assigned to the exec profile.
3. Link the current predecessor to the fix task.
4. Link the fix task as a parent of the blocked review task.
5. Unblock the review task.
6. Because the new fix parent is not done yet, `unblock_task` sends review back to `todo` rather than immediately `ready`.
7. When fix completes, Hermes `recompute_ready` promotes review to `ready`, and the dispatcher reruns the same review task.

Important: both `fix -> review` and `unblock review` are required. Only creating the fix task does not rerun review; only unblocking review without the new dependency may rerun too early.

## Multi-Round Fixes

For later review failures, keep inserting fix tasks before the same review gate:

```text
root -> exec -> fix-1 -> fix-2 -> review
```

Each review attempt stays in the review task's runs/comments. The graph expresses the current effective path to the gate.

Use an automatic loop cap, typically two fix insertions before orchestrator triage. After the cap, Mochi should decide whether to clarify the root spec, rewrite the fix task, adjust review scope, use a stronger model/profile, or ask the user.

## Semantics

- `blocked` does not automatically mean the user must answer. Mochi triages first.
- `done` on exec means implementation handoff is complete.
- `done` on review means the gate passed or the review task explicitly completed under a defined workflow; failed review should not be marked done merely to move the graph forward.
- Comments are the attempt/audit timeline; task links are the executable dependency path.
- Root task body remains the spec SSOT. If a block resolution changes effective requirements, update the root body, not only comments.
