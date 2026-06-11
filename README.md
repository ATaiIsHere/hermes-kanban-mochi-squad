# Hermes Kanban Mochi Squad

Mochi Squad is a skill-only workflow package for modeling project-oriented, multi-agent work on top of native Hermes Kanban.

Version `0.1.0` ships reusable workflow docs plus deterministic setup/readiness scripts. It is not a daemon, server, Virtual Office API, or fork of Hermes Kanban; watcher cron installation remains an explicit operator action.

## What v0.1 provides

- A Hermes skill at `skills/mochi-squad/SKILL.md`.
- Orchestrator guidance for turning a request into a native Kanban task graph.
- Setup/readiness scripts for planning, installing, verifying, and conservatively repairing a local runtime.
- Minimal profile `SOUL.md` templates for core `mochi-exec` and `mochi-review`, plus optional/future `mochi-research`.
- A Project convention derived from existing Kanban task links.
- Blocked recovery patterns for exec rerun and review fix insertion without marking failed work done.

## Non-goals

Mochi Squad v0.1 does not:

- modify the Hermes Kanban database schema;
- introduce custom task columns or Mochi-only task metadata;
- implement a daemon, web server, Virtual Office UI, or Virtual Office API;
- install services, cron jobs, credentials, DNS, tunnels, or proxies automatically;
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
      profiles/
        README.md
        mochi-exec/
          SOUL.md
        mochi-review/
          SOUL.md
        mochi-research/
          SOUL.md
    scripts/
      blocked-watchdog.py
      check_readiness.py
      setup.py
examples/
  basic-linear-workflow.md
  review-fix-re-review.md
  block-rerun-and-fix-insertion.md
tests/
  test_blocked_watchdog.py
  test_config_parse.py
  test_readiness.py
  test_setup.py
```

## Setup / readiness

The skill can be useful even when no local runtime has been installed. Runtime setup is explicit and side-effect-aware:

```bash
python skills/mochi-squad/scripts/setup.py --plan
python skills/mochi-squad/scripts/setup.py --install
python skills/mochi-squad/scripts/setup.py --verify
python skills/mochi-squad/scripts/setup.py --repair
```

Setup creates missing runtime files under `${HERMES_HOME}/mochi-squad/`, creates missing core profiles (`mochi-exec`, `mochi-review`), installs the `mochi-squad` skill into worker profile skill directories, writes recommended profile config only for newly-created profiles, and records generated facts in `state.yaml`. Existing SOUL/config files are audited and skipped, not overwritten.

`blocked-watchdog.py` is deterministic and quiet: no new blocked events means empty stdout, suitable for a Hermes `no_agent=true` cron. Cron creation and notification target selection remain explicit/operator-approved.

## Installing the skill

Copy or symlink `skills/mochi-squad` into your Hermes skills directory, then load the `mochi-squad` skill in an agent session.

Profile templates are examples for explicit installation only. They should not overwrite existing Hermes profiles by default, and the detailed workflow rules remain in `SKILL.md` and `references/*.md` rather than duplicated into SOUL files.
