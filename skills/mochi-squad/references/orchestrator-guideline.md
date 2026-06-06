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
elif graph contains an unresolved blocked task:
  Project = BLOCKED
elif all leaf tasks are done or archived:
  Project = DONE
else:
  Project = IN_PROGRESS
```

`unresolved blocked task` means a blocked task without a completed resolve-block or resolve-review-block continuation path.

The main lane should stay simple. A project detail view can show native task statuses, current assignees, run summaries, review results, artifacts, blocked reasons, and the recovery path.

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
- blocked event reason;
- task position in the project graph.

If the available evidence does not determine the correct action, stop and ask for the missing decision through the normal human-in-the-loop path. Do not invent scope, acceptance criteria, credentials, permissions, or user-facing behavior.

## Rerun Original Task

Rerun the original blocked task when it remains the correct work item:

- goal, scope, acceptance criteria, and target scenarios are unchanged;
- the same assignee should perform the same work;
- no new dependency branch is needed;
- missing context fits as a comment or small supplement;
- existing downstream tasks remain valid.

Flow:

```text
blocked task
  -> supplement with missing context
  -> unblock/rerun original task
  -> original task completes
  -> existing child tasks dispatch
```

## Resolve-Block Branch

Use a resolve-block branch when the original task should remain blocked as historical fact and workflow must continue through a new path.

Use this when:

- goal, scope, acceptance criteria, or scenarios changed;
- the original task is no longer the correct executable unit;
- a different task type, assignee, or dependency path is needed;
- recovery itself should be visible in the project graph.

Flow:

```text
blocked exec remains blocked
  -> resolve-block task records the decision or resolution
  -> replacement exec/review path continues
```

The resolve-block task should record why the original task remains blocked, what decision was made, and what task should run next.

## Failed Review / Review Blocked

A failed review should not be marked done. Preserve it as blocked evidence and continue through a review-specific bridge:

```text
blocked review remains blocked
  -> resolve-review-block task records failed scenarios
  -> fix exec task
  -> re-review task
```

The fix task should target only the failed scenarios unless the root specification is explicitly changed. The re-review task should verify the failed scenarios and any regression checks needed for safety.

## Virtual Office Boundary

Virtual Office is deferred in v0.1. A future UI may read the native task graph and show projects, lanes, chains, blockers, and artifacts. API routes, response shape, server lifecycle, and visual behavior are intentionally not specified here.

Until that design exists, Mochi Squad only promises that the information needed by a future Virtual Office can be derived from native Kanban data and task handoffs.

## Notification Boundary

Human-intervention notifications should be configurable by the local runtime. Do not hardcode a platform, channel, chat id, webhook URL, or local deployment path in reusable skill documentation.

## Authentication Boundary

For GitHub automation, prefer selected-repository GitHub App installation access, such as an app named `mochi-squad`, over broad personal PATs. Store private keys and short-lived tokens outside the repository and never include them in task bodies, comments, committed files, logs, or examples.
