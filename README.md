# Hermes Kanban Mochi Squad

Mochi Squad is a skill-only workflow package for modeling project-oriented, multi-agent work on top of native Hermes Kanban.

Version `0.1.0` is intentionally small: it ships reusable skill documentation and conventions. It is not a daemon, server, scheduler replacement, Virtual Office API, or fork of Hermes Kanban.

## What v0.1 provides

- A Hermes skill at `skills/mochi-squad/SKILL.md`.
- Orchestrator guidance for turning a request into a native Kanban task graph.
- Setup/readiness guidance for separating reusable skill content from local runtime state.
- A Project convention derived from existing Kanban task links.
- Blocked recovery patterns for exec rerun and review fix insertion without marking failed work done.

## Non-goals

Mochi Squad v0.1 does not:

- modify the Hermes Kanban database schema;
- introduce custom task columns or Mochi-only task metadata;
- implement a daemon, web server, Virtual Office UI, or Virtual Office API;
- install services, cron jobs, profiles, or credentials automatically;
- require broad personal GitHub PATs for repository automation.

## Project model

A Mochi Squad Project is:

```text
Project = root task + all descendants
```

The root task is the planning/spec anchor. All implementation, review, fix, and recovery work is linked below it using native Hermes Kanban parent/child task links.

Project state is derived from the native task graph:

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

An unresolved blocked task is a task still in `blocked` after Mochi triage, usually waiting on orchestrator, user, environment, credentials, or unsafe-operation approval. Normal review `needs_fix` blocks should be converted into fix insertion and unblocked. Project details can show the task chain, assignees, run summaries, review results, artifacts, blocked reasons, rerun/resume comments, and fix-insertion history from native task fields, comments, events, and handoffs.

## Standard workflow

A typical linear workflow is:

```text
root/spec task
  -> exec task
  -> review task
```

The root task should carry the durable contract: goal, scope, non-goals, user stories, scenarios, acceptance criteria, verification strategy, and block policy. Child tasks should reference the root task and target scenarios instead of copying the whole spec.

## Blocked recovery

Do not mark blocked or failed work as done just to unblock downstream tasks. Use the original task whenever it is still the right executable unit.

For an execution block:

```text
exec block -> add resume-context -> unblock same exec -> rerun
```

Reruns are not necessarily from scratch. The blocked exec should record completed work, remaining work, attempted fixes, artifacts or changed files, `do_not_repeat`, and a resume hint.

For a failed review:

```text
root -> exec -> review(blocked: needs_fix)
root -> exec -> fix -> review(unblocked, waiting on fix)
fix done -> review auto-promotes/reruns
```

The review task is the gate. Mochi inserts a scoped fix task before the same review task, links `fix -> review`, then unblocks review. Native dependency promotion reruns review when the fix completes.

See `skills/mochi-squad/references/block-rerun-and-fix-insertion.md`.

## Virtual Office boundary

Virtual Office is a future extension. v0.1 only guarantees that enough information can be derived from the native Kanban graph and task handoffs for a future UI. API routes, response shapes, server behavior, and visual presentation are deliberately deferred until the UI and product decisions are made.

## GitHub authentication guidance

For repository automation, prefer a GitHub App installation with selected-repository access, such as an app named `mochi-squad`, over broad personal PATs. The installation should request only the permissions needed for the task, commonly metadata read plus contents, pull requests, issues, and actions access as required.

Never commit app private keys, installation tokens, personal access tokens, runtime state, local notification targets, or generated logs.

## Repository layout

```text
README.md
LICENSE
CHANGELOG.md
.gitignore
skills/
  mochi-squad/
    SKILL.md
    references/
      orchestrator-guideline.md
      block-rerun-and-fix-insertion.md
      pr-handoff-guard-policy.md
      setup-readiness.md
    templates/
      mochi-squad.config.yaml
    scripts/
      check_readiness.py
      setup.py
examples/
  basic-linear-workflow.md
  review-fix-re-review.md
  block-rerun-and-fix-insertion.md
tests/
  test_readiness.py
  test_config_parse.py
```

Future versions may add templates, readiness scripts, tests, and examples while keeping the core rule intact: Mochi Squad is a convention layer over native Hermes Kanban, not a schema fork.

## Installing the skill

Copy or symlink `skills/mochi-squad` into your Hermes skills directory, then load the `mochi-squad` skill in an agent session.

The skill can be useful even when no local runtime has been installed. Runtime setup, watchers, profiles, or dashboards should be explicit opt-in steps documented separately and verified before use.
