# Project Graph Conventions

A Mochi Squad Project is derived from native Hermes Kanban:

```text
Project = root task + all descendants
```

No custom database schema, columns, or Mochi-only task metadata are required.

## State Derivation

```text
if root.status == triage:
  Project = PLANNING
elif graph contains a blocked task that still needs orchestrator/user/external intervention:
  Project = BLOCKED
elif all leaf tasks are done or archived:
  Project = DONE
else:
  Project = IN_PROGRESS
```

Definitions:

- root task: planning/spec anchor.
- descendant: any task reachable through native parent/child links.
- leaf task: descendant with no children.
- unresolved blocked task: still blocked after Mochi triage, usually waiting on orchestrator, user, environment, credentials, permissions, or unsafe-operation approval.

Normal review `needs_fix` blocks should be converted into fix insertion and unblocked; they should not leave the whole Project permanently blocked.

## Task Graph Patterns

Linear path:

```text
root/spec -> exec -> review
```

Review fix insertion:

```text
root -> exec -> review(blocked: needs_fix)
root -> exec -> fix -> review(unblocked, waiting on fix)
fix done -> review reruns
```

Exec rerun:

```text
exec(blocked) -> add resume-context -> unblock same exec -> rerun
```

## Evidence Surfaces

Use native fields and records:

- task body;
- parent/child links;
- task status;
- comments;
- events;
- run summaries;
- run metadata;
- handoff artifacts.
