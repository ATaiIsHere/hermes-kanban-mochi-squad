# Example: resolve-block flow

Use this flow when an execution task blocks and the original task is no longer the right executable unit. Keep the original task blocked and continue through a `resolve-block` task.

If the original task is still correct and only needs a small missing detail, supplement and rerun it instead. Use this example when the path changes.

## Task graph

```text
T1 root/spec: "Create workflow examples"
  -> T2 exec: "Generate examples from an old draft"     [blocked: source draft unavailable]
     -> T3 resolve-block: "Choose replacement source and narrow scope"  [done]
        -> T4 exec: "Write examples from the root scenarios"
           -> T5 review: "Verify examples against root scenarios"
```

`T2` stays blocked because it cannot complete as originally written. `T3` records the decision that replaces the old execution path.

## Original exec block comment

```markdown
Task `T2` cannot continue as written.

Reason:
- The body depends on an external draft that is not available in this repository.
- Re-running the same task would fail again.

Impact:
- The root goal is still valid.
- The execution approach should change: write examples directly from the root scenarios instead of from the missing draft.
```

## Block reason

```text
Original source draft is unavailable; task should be replaced by a scenario-based exec path.
```

## Resolve-block task body

```markdown
# Purpose
Resolve blocked exec task `T2` while preserving its blocked history.

# Decision
Keep `T2` blocked. Replace the execution path with a new task that writes examples directly from root scenarios S1-S3.

# New execution scope
Create concise examples for:
- basic linear flow;
- review-fix-rereview flow;
- resolve-block flow.

# Constraints
- Use native Hermes Kanban task links and statuses only.
- Do not introduce custom database fields.
- Do not mention private paths, private users, tokens, job IDs, or local deployment assumptions.

# Next task
Create a new exec task under this resolve-block task, followed by review.
```

When `T3` completes, child task `T4` can run. The graph still shows that `T2` blocked, but the project has a documented continuation path.

## Replacement exec task body

```markdown
Using root task `T1` and resolve-block task `T3`, write the examples directly from the accepted scenarios.

Deliverables:
- `examples/basic-linear.md`
- `examples/review-fix-rereview.md`
- `examples/resolve-block.md`

Each example must:
- show Project = root task + descendants;
- use native Kanban parent/child links;
- preserve blocked or failed history through a resolve task;
- stay public-friendly and self-contained.
```

## Review task body

```markdown
Verify examples from `T4` against root `T1` and resolve-block `T3`.

Checklist:
- [ ] Basic linear example is easy to follow.
- [ ] Review-fix-rereview example keeps failed review blocked.
- [ ] Resolve-block example keeps original exec blocked and continues through a resolve-block task.
- [ ] Every example models Project as root task + descendants.
- [ ] No custom Hermes Kanban DB fields are introduced.
- [ ] No Virtual Office API, local service, token, job ID, private target, or local path assumptions appear.
```

## Choosing rerun vs resolve-block

```text
Supplement + rerun original exec when:
- scope is unchanged;
- the original task is still the right work item;
- a missing detail or transient failure caused the block.

Branch through resolve-block when:
- scope or approach changes;
- the original task would fail again;
- the new path should be visible in the project graph.
```
