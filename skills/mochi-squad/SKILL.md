---
name: mochi-squad
description: Use when modeling project-oriented multi-agent workflows on top of Hermes Kanban without changing the native Kanban schema; covers Project derivation, orchestrator routing, blocked recovery, readiness boundaries, and future Virtual Office constraints.
version: 0.1.0
author: Mochi Squad contributors
license: MIT
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, workflow, review, recovery]
    related_skills: [kanban-worker]
---

# Mochi Squad

## Overview

Mochi Squad is a skill-only convention layer for Hermes Kanban. It explains how to organize native Kanban tasks into durable project workflows, how an orchestrator should route plan/exec/review work, and how to continue safely when execution or review is blocked.

Version `0.1.0` is documentation-only. It does not run a daemon, expose a server, install a Virtual Office, modify Hermes Kanban schema, or require custom task columns.

## When to Use

Use this skill when:

- turning a request into a durable Hermes Kanban task graph;
- explaining or implementing `Project = root task + descendants`;
- deriving project lanes from native task states and task links;
- designing plan -> exec -> review workflows;
- deciding whether a blocked exec should rerun in place or a blocked review should receive a fix insertion;
- documenting setup/readiness boundaries for a local Mochi Squad runtime;
- preparing for a future Virtual Office without committing to API shapes yet.

Do not use this skill to bypass Hermes Kanban, mutate its database schema, install services implicitly, or treat a failed review as done.

## Core Principles

1. Mochi Squad is a convention layer over native Hermes Kanban.
2. A Project is the root task plus every descendant reachable through native task links.
3. The root task is the specification source of truth.
4. Child tasks reference root scenarios instead of duplicating the full spec.
5. Review verifies scenarios and records evidence; it should not become implementation work.
6. Blocked tasks are triaged by Mochi first; ordinary review `needs_fix` is resolved by fix insertion, not by permanently preserving a blocked review.
7. Local runtime state belongs outside reusable skill files.
8. Virtual Office API and response shape are deferred until UI decisions are made.

## Project State Derivation

Virtual Office or reporting tools may show four project lanes:

```text
PLANNING | IN_PROGRESS | BLOCKED | DONE
```

Derive them from native Kanban state:

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

- `root task`: the planning/spec anchor for the project.
- `descendant`: any task reachable from the root through native parent/child task links.
- `leaf task`: a descendant with no children.
- `unresolved blocked task`: a task still in `blocked` after Mochi triage, usually waiting on orchestrator, user, environment, credentials, or unsafe-operation approval. Normal review `needs_fix` blocks should be converted into fix insertion and unblocked.

Do not add Mochi-only database fields to compute this. Read native task status, task links, comments, events, run summaries, and run metadata.

## Orchestrator Workflow

The orchestrator should keep the root task as the durable work contract. A good root task includes:

- goal;
- scope and non-goals;
- user stories;
- scenarios or acceptance criteria;
- verification strategy;
- planned task graph;
- handoff requirements;
- block policy.

A simple linear graph:

```text
root/spec
  -> exec
  -> review
```

A larger graph may fan out research or spikes, then fan in to synthesis, implementation, and review. Children should stay focused on their role and reference the root task plus scenario IDs.

## Blocked Recovery

Before routing recovery, inspect the blocked task body, parent handoff, comments, run summary, run metadata, typed block reason, and graph position.

Do **not** create resolve-block tasks for the normal Mochi workflow. A blocked task should usually be resolved in place:

```text
exec block   -> add resume-context -> unblock same exec -> rerun
review block -> insert fix before review -> unblock same review -> fix done reruns review
```

Exec blocks usually mean the worker needs more context, environment recovery, narrower instructions, or an orchestrator/user decision. Keep the original exec task as the executable unit when the goal/scope/scenarios are still correct. Add a structured `[resume-context]` comment and unblock the same exec task so the rerun can continue from recorded progress instead of starting from scratch.

For failed review, use Review-Blocked Fix Insertion. The review task is the gate:

```text
root -> exec -> review
root -> exec -> review(blocked: needs_fix)
root -> exec -> fix -> review(unblocked, waiting on fix)
fix done -> review auto-promotes/reruns
```

Both `fix -> review` and `unblock review` are required. Only creating the fix task does not rerun review; only unblocking review without the new dependency may rerun too early.

Never mark failed execution or failed review as done merely to release downstream dependencies. If the original task is no longer the correct work item, stop and replan with an explicit root-spec update or replacement branch.

See `references/block-rerun-and-fix-insertion.md` for typed block reasons, comment shapes, and multi-round fix rules.

## Setup and Readiness Boundary

The skill package and the local runtime are separate:

```text
skill package = reusable docs, templates, schemas, scripts
runtime install = local config, state, profiles, watchers, services
```

Loading this skill should provide workflow knowledge. It should not silently install, repair, restart, or modify the host.

See `references/setup-readiness.md` for the recommended runtime directory, readiness states, and explicit setup command boundaries.

## Profile Templates

Profile templates live under `templates/profiles/<profile>/SOUL.md`. They are intentionally minimal: identity, role boundaries, and a pointer back to this skill and the relevant references.

Core templates:

- `templates/profiles/mochi-exec/SOUL.md`
- `templates/profiles/mochi-review/SOUL.md`

Optional templates:

- `templates/profiles/mochi-research/SOUL.md`
- `templates/profiles/mochi-plan/SOUL.md` — optional fallback only; the normal planning path is the conversation orchestrator plus the root task as SSOT.

Do not duplicate long operational rules into profile SOUL files. If a role must follow a rule, route it from `SKILL.md` and keep the detailed rule in `references/*.md`.

## Virtual Office Boundary

Virtual Office is a future extension. v0.1 only defines the derivation contract: project state and details must be recoverable from the native Kanban graph and handoff records.

Do not define committed API routes, response shapes, or server behavior in v0.1. Those should be designed when the UI and product needs are known.

## GitHub App Access

For repository-scoped automation, prefer a GitHub App installation with selected repository access, such as an app named `mochi-squad`, over broad personal PATs. Use the minimum required permissions and never commit private keys, installation tokens, personal tokens, local runtime state, or notification targets.

## References

- `references/orchestrator-guideline.md` — project graph, orchestration, exec rerun, and review fix-insertion conventions.
- `references/block-rerun-and-fix-insertion.md` — typed block reasons, exec rerun comments, and review fix insertion.
- `references/pr-handoff-guard-policy.md` — guard-safe PR handoff format for retryable Kanban comments.
- `references/setup-readiness.md` — package/runtime separation and readiness model.
- `templates/profiles/` — minimal SOUL templates for core and optional Mochi worker profiles.

## Common Pitfalls

1. Treating Project as a new Kanban database table. It is not; it is derived from the native task graph.
2. Copying the full root spec into every child task. Reference root scenarios instead.
3. Marking blocked or failed work done to keep the graph moving. Use exec rerun or review fix insertion instead; preserve history in comments/runs.
4. Installing services just because the skill was loaded. Runtime installation must be explicit.
5. Defining Virtual Office API shape too early. v0.1 deliberately defers it.
6. Using broad personal PATs where a selected-repository GitHub App installation would be safer.
7. Adding profile templates that become a second manual. Keep SOUL files thin; route detailed behavior through this skill and references.

## Verification Checklist

- [ ] Root task is the project anchor.
- [ ] Project lanes can be derived without schema changes.
- [ ] Root task carries scope, non-goals, stories, scenarios, verification, and block policy.
- [ ] Child tasks reference root scenarios and stay role-focused.
- [ ] Blocked recovery uses rerun only when the original task remains correct.
- [ ] Failed review uses fix insertion before the same review gate and scopes fixes to failed scenarios.
- [ ] Skill docs do not commit local runtime state, secrets, or host-specific paths.
- [ ] Profile templates exist for core workers and stay minimal.
- [ ] Virtual Office is described as future work with API/response shape deferred.
