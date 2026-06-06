# Example: review-fix-rereview flow

Use this flow when implementation finishes but review finds a blocking issue. The failed review remains blocked as historical evidence. The project continues through a `resolve-review-block` task, a focused fix task, and a re-review task.

## Task graph

```text
T1 root/spec: "Document a workflow convention"
  -> T2 exec: "Implement docs and examples"
     -> T3 review: "Verify scenarios S1-S3"        [blocked: failed review]
        -> T4 resolve-review-block: "Record review decision and continuation path"  [done]
           -> T5 fix: "Fix failed review items only"
              -> T6 re-review: "Re-verify failed items from T3"
```

`T3` is not marked done just to unblock the fix. The blocked review remains visible in the project graph, and `T4` records why the workflow can continue. The graph uses native Hermes Kanban task links and statuses only; it does not require custom fields or schema changes.

## Failed review task comment

```markdown
Review result for `T3`:

Failed items:
- S2: The docs mention projects but do not state that Project = root task + descendants.
- S3: The blocked recovery section says to mark failed reviews done, which would erase failure history.

Evidence:
- `README.md` has no project derivation section.
- `references/orchestrator-guideline.md` describes review failure recovery incorrectly.
```

## Block reason

```text
Failed review: project derivation is incomplete and review-failure recovery would erase blocked history.
```

Keep the block reason short. Put the detailed checklist and evidence in a comment.

## Resolve-review-block task body

```markdown
# Purpose
Resolve blocked review task `T3` without marking it done.

# Decision
The review failure is valid. Keep `T3` blocked as historical evidence.
Continue through a focused fix and re-review branch.

# Fix scope
Only address failed items from `T3`:
- Add clear Project = root task + descendants wording.
- Replace any instruction that marks failed review done with resolve-review-block -> fix -> re-review.

# Next task
Create a fix task under this task, then a re-review task under the fix task.
```

When this task completes, its child fix task can dispatch without pretending `T3` passed.

## Fix task body

```markdown
Fix failed review task `T3` as resolved by `T4`.

Allowed changes:
- Edit docs/examples needed to pass the failed checklist items.

Not allowed:
- Expand the v0.1 scope.
- Add server, UI, daemon, or custom Kanban DB fields.
- Rewrite unrelated docs.

Before completing, comment with:
- changed files;
- exact failed items addressed;
- self-check evidence.
```

## Re-review task body

```markdown
Re-verify only the failed items from blocked review `T3`, using fix task `T5` and resolve-review-block task `T4` as context.

Checklist:
- [ ] Docs clearly say Project = root task + descendants.
- [ ] Docs preserve failed review history with resolve-review-block -> fix -> re-review.
- [ ] Blocked `T3` remains blocked and is not represented as passed work.
- [ ] Fix did not introduce custom Kanban DB fields or local-only assumptions.

Complete this task only if all re-review items pass.
```

## Why this pattern exists

Hermes Kanban dependencies naturally wait for parent tasks to finish. Mochi Squad uses a completed resolve task as the continuation point, while the original failed review remains blocked. That gives both properties:

- accurate history: failed review is still visible;
- forward progress: fix and re-review can continue from the resolve task.
