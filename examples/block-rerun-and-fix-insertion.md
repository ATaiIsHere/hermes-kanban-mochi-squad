# Block / Rerun / Fix Insertion Example

This example shows the normal Mochi Squad recovery path without creating resolve-block tasks.

## Exec block rerun

Initial graph:

```text
root -> exec -> review
```

If exec blocks because it needs context or environment recovery:

```text
root -> exec(blocked)
```

The orchestrator triages the block, adds a resume comment, and unblocks the same exec task:

```text
[resume-context]
for_task: t_exec
for_attempt: 2
decision_or_context:
- Use option B for the missing setting.
continue_from:
- Keep the files already created in attempt 1.
do_not_repeat:
- Do not re-scaffold the project.
next_steps:
- Finish the remaining target scenarios and self-check.
root_spec_updated: no
```

Then:

```text
root -> exec(unblocked/rerun) -> review
```

The exec rerun reads prior comments and continues from recorded progress.

## Review fix insertion

If review finds fixable failed scenarios:

```text
root -> exec -> review(blocked: needs_fix)
```

The review comment records evidence:

```text
[review-block]
attempt: 1
reason_type: needs_fix
result: failed
failed_scenarios:
- S-1.2: expected X, observed Y
evidence:
- command/output/screenshot path
recommended_fix_scope:
- Change only the S-1.2 behavior.
non_goals:
- Do not redesign unrelated flows.
```

The orchestrator inserts a fix before the same review gate:

```text
root -> exec -> fix -> review(unblocked, waiting on fix)
```

Operation order:

1. Create `fix` with parent = the current review predecessor.
2. Link `fix -> review`.
3. Unblock review.
4. Because `fix` is not done, review returns to `todo`.
5. When fix completes, review auto-promotes to `ready` and reruns.

## Why this works

Hermes promotes `todo` children when all parents are `done`. `unblock_task` also respects parent completion: if the newly linked fix parent is not done, the unblocked review waits in `todo` instead of running too early.

## Loop cap

If repeated review attempts keep producing `needs_fix`, cap automatic fix insertion, typically after two fix tasks:

```text
root -> exec -> fix-1 -> fix-2 -> review
```

After the cap, the orchestrator should triage whether the root spec is unclear, the fix task was too vague, the reviewer scope is wrong, a stronger model/profile is needed, or a user decision is required.
