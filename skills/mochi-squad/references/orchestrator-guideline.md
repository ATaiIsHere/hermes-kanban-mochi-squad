# Mochi Squad Orchestrator Guideline

Status: v0.1 draft for a skill-only Hermes Kanban extension.

## Scope

The orchestrator coordinates durable multi-agent work using native Hermes Kanban tasks, links, comments, events, summaries, and metadata. Mochi Squad does not change the Hermes Kanban database schema and does not require Mochi-only task fields.

## Project Model

```text
Project = root task + all descendants
```

The root task is the planning/specification anchor. Every implementation, review, fix, recovery, and re-review task should be linked under that root through native parent/child task links.

## Project Lanes

Mochi Squad uses four main project lanes:

```text
PLANNING | IN_PROGRESS | BLOCKED | DONE
```

Derived status:

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

`unresolved blocked task` means a task still in `blocked` after Mochi triage, usually waiting on orchestrator, user, environment, credentials, or unsafe-operation approval. Normal review `needs_fix` blocks should be converted into fix insertion and unblocked.

The main lane should stay simple. A project detail view can show native task statuses, current assignees, run summaries, review results, artifacts, typed blocked reasons, rerun/resume comments, and fix-insertion history.

## Root Task Contract

The root task should be the single source of truth for the project specification. It should capture:

- goal;
- scope and non-goals;
- user stories;
- scenarios or acceptance criteria;
- verification strategy;
- intended task graph;
- handoff requirements;
- block policy.

Downstream tasks should reference the root and specific scenarios. Avoid copying the whole root specification into every child task.

## Standard Flow

Linear workflow:

```text
root/spec done
  -> exec task
  -> review task
```

Parallel workflow:

```text
root/spec done
  -> research/spike tasks in parallel
  -> synthesis task
  -> exec task
  -> review task
```

The dependency graph should express execution order. Children wait for parent completion using native Hermes Kanban dependency behavior.

## Blocked Task Triage

Before deciding a recovery path, inspect:

- blocked task body;
- parent handoff;
- comment thread;
- run summary and metadata;
- typed blocked event reason;
- task position in the project graph;
- workspace evidence when relevant.

If the available evidence does not determine the correct action, stop and ask for the missing decision through the normal human-in-the-loop path. Do not invent scope, acceptance criteria, credentials, permissions, risk, cost, or user-facing behavior.

## No Resolve-Block by Default

Do not create resolve-block tasks for the normal Mochi workflow. A blocked task should usually be resolved in place:

```text
exec block   -> add resume-context -> unblock same exec -> rerun
review block -> insert fix before review -> unblock same review -> fix done reruns review
```

Historical detail belongs in comments and run records. Task links should express the current executable dependency path.

## Exec Block Rerun

Rerun the original blocked exec task when it remains the correct work item:

- goal, scope, acceptance criteria, and target scenarios are unchanged;
- the same assignee should perform the same work;
- missing context fits as a comment, small supplement, or root spec update;
- existing downstream tasks remain valid.

Flow:

```text
blocked exec
  -> orchestrator adds [resume-context] / supplement / recovery note
  -> unblock and rerun original exec
  -> original exec continues from recorded progress
  -> original exec done
  -> existing child tasks dispatch
```

Exec block comments should record completed work, remaining work, attempted fixes, artifacts/changed files, `do_not_repeat`, and `resume_hint`. Mochi resume comments should record the decision/context, where to continue, what not to repeat, next steps, and whether root spec changed.

If the original exec is no longer the correct work item, stop and replan. Do not pretend the blocked exec succeeded. Update the root spec, explain the supersession in comments, and create a replacement branch only after deciding how to keep downstream dependencies honest.

## Review-Blocked Fix Insertion

A failed review should not be marked done merely to move the graph forward. The review task is the gate.

Flow:

```text
root -> exec -> review
root -> exec -> review(blocked: needs_fix)
root -> exec -> fix -> review(unblocked, waiting on fix)
fix done -> review auto-promotes/reruns
```

Operation order:

1. Review blocks with typed reason `needs_fix` and comments failed scenarios/evidence.
2. Mochi creates a scoped fix task assigned to exec.
3. Link the current predecessor to the fix task.
4. Link the fix task as a parent of the blocked review task.
5. Unblock the review task. Because the new fix parent is not done, review waits in `todo`.
6. When fix completes, native dependency promotion reruns the same review task.

Fix normally scopes to failed scenarios only. Use an automatic loop cap, typically two fix insertions, before orchestrator triage.

See `block-rerun-and-fix-insertion.md` for typed block reasons, comment templates, and multi-round rules.

## Virtual Office Boundary

Virtual Office is deferred in v0.1. A future UI may read the native task graph and show projects, lanes, chains, blockers, and artifacts. API routes, response shape, server lifecycle, and visual behavior are intentionally not specified here.

Until that design exists, Mochi Squad only promises that the information needed by a future Virtual Office can be derived from native Kanban data and task handoffs.

## Notification Boundary

Human-intervention notifications should be configurable by the local runtime. Do not hardcode a platform, channel, chat id, webhook URL, or local deployment path in reusable skill documentation.

## Authentication Boundary

For GitHub automation, prefer selected-repository GitHub App installation access, such as an app named `mochi-squad`, over broad personal PATs. Store private keys and short-lived tokens outside the repository and never include them in task bodies, comments, committed files, logs, or examples.
