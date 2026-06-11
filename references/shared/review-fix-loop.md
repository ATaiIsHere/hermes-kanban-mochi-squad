# Review Fix Loop and Block Rerun Policy

This reference defines the normal Mochi recovery path for exec blocks and review `needs_fix` without creating resolve-block tasks.

## Core Rule

```text
exec block   -> add resume-context -> unblock same exec -> rerun
review block -> insert fix before same review -> unblock same review -> fix done reruns review
```

Do not mark failed execution or failed review as done just to release dependencies.

## Exec Block Rerun

Use the same exec task when the original goal/scope/scenarios remain correct. The orchestrator adds a `[resume-context]` comment and unblocks the same exec task.

Required resume context:

```text
[resume-context]
completed:
remaining:
tried:
artifacts_or_changed_files:
do_not_repeat:
resume_hint:
block_reason:
```

Create a replacement branch only if the root spec or executable unit is no longer correct.

## Review needs_fix

The review task is the gate. When implementation fails review:

1. Review blocks with typed reason `needs_fix` and evidence.
2. Orchestrator creates a scoped fix task under the implementation path.
3. Orchestrator links `fix -> same review`.
4. Orchestrator unblocks review so native dependencies keep it waiting until fix completes.
5. Fix done promotes/reruns the same review gate.

Both `fix -> review` and `unblock review` are required. Only creating the fix task does not rerun review; only unblocking review without the dependency may rerun too early.

## needs_fix Block Shape

```text
reason: needs_fix
failed_scenarios:
evidence:
expected:
actual:
fix_scope:
out_of_scope:
```

## Multi-Round Fixes

A second `needs_fix` may create another scoped fix if the failure is concrete and bounded. If repeated fixes show unclear requirements or unsafe scope drift, the orchestrator should update the root spec or ask the user.
