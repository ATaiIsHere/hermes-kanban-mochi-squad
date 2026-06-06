# Example: basic linear project flow

Use this flow when the work can move through one implementation task and one verification task.

## Task graph

```text
T1 root/spec: "Publish a small skill package"
  -> T2 exec: "Implement the package files"
     -> T3 review: "Verify the package against the root scenarios"
```

`T1` is the project anchor. The project is `T1` plus every descendant reachable through native parent/child links.

## Root/spec task body

```markdown
# Goal
Publish a small Hermes skill package that documents one workflow convention.

# Scope
- Add README, skill file, references, examples, and tests.
- Keep the package documentation-only for v0.1.

# Non-goals
- Do not modify Hermes native Kanban schema.
- Do not add a daemon, API server, or UI.

# Scenarios
S1 — Installable skill docs
Given a user clones the repo,
when they inspect the skill file,
then the skill explains the workflow and links to references.

S2 — Project derivation
Given the user opens the task graph,
when they follow root and descendants,
then project status can be derived without custom fields.

# Verification
- Confirm all required files exist.
- Confirm docs mention native Kanban tasks and parent/child links.
- Confirm no private runtime state or local-only paths are committed.
```

## Exec task body

```markdown
Implement the files required by root task `T1`.

Focus only on scenarios S1 and S2.
Do not expand scope beyond the root/spec task.
Record changed files and commands run in a task comment before completing.
```

Suggested dependency: create `T2` with `parents=[T1]`. When `T1` is done, the dispatcher can promote `T2`.

## Review task body

```markdown
Verify exec task `T2` against root task `T1`.

Checklist:
- [ ] Required files exist.
- [ ] Docs define Project as root task + descendants.
- [ ] Docs use native Kanban fields and dependency links only.
- [ ] No custom Kanban database fields are introduced.
- [ ] No private identifiers, secrets, or local-only paths appear.

If every item passes, complete the review.
If any item fails, block the review with the failed checklist items.
```

Suggested dependency: create `T3` with `parents=[T2]`. Do not start review until exec is done.

## Status derivation

```text
PLANNING     T1 is still being clarified or triaged.
IN_PROGRESS  At least one child task is todo, ready, or in_progress.
BLOCKED      A graph task is blocked and has no completed resolve path.
DONE         All leaf tasks are done or archived.
```

This is a convention layer over Hermes Kanban, not a schema change.
