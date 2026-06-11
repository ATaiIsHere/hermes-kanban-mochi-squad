# Mochi Squad Setup and Readiness

Status: v0.1 setup contract.

## Purpose

This document separates reusable skill content from local runtime installation state and defines what the deterministic setup scripts own.

```text
skill package = reusable docs, templates, examples, tests, side-effect-aware scripts
runtime install = local config, state, profiles, watcher script copy, cron wiring, logs/cache
```

Loading the skill should give an agent workflow knowledge. It should not silently install dependencies, create profiles, create cron jobs, start services, rewrite config, or repair the host. Setup changes happen only through explicit setup commands.

## Skill Package Layout

```text
skills/mochi-squad/
  SKILL.md
  references/
    user-stories.md
    orchestrator-guideline.md
    block-rerun-and-fix-insertion.md
    pr-handoff-guard-policy.md
    setup-readiness.md
  templates/
    mochi-squad.config.yaml
    profiles/
      README.md
      mochi-exec/SOUL.md
      mochi-review/SOUL.md
      mochi-research/SOUL.md      # optional/future
  scripts/
    blocked-watchdog.py
    check_readiness.py
    setup.py
```

There is no core `mochi-plan` template. Normal planning is owned by the conversation orchestrator and root task SSOT.

## Runtime Layout

Runtime files live outside reusable skill files:

```text
${HERMES_HOME}/mochi-squad/
  config.yaml
  state.yaml
  scripts/
    blocked-watchdog.py
  blocked-watchdog-state.json
  logs/
  cache/
```

Definitions:

- `config.yaml`: stable desired local deployment settings copied from a template.
- `state.yaml`: JSON-compatible YAML recording observed/generated facts from setup/verify/repair/watchers.
- `scripts/`: copied deterministic scripts used by local runtime or cron jobs.
- `blocked-watchdog-state.json`: dedupe state for blocked event notifications.
- `logs/` and `cache/`: disposable runtime data.

Do not store raw secrets, API tokens, OAuth credentials, private keys, personal data, local chat ids, or webhook URLs in committed files. Config may refer to secret locations or environment variable names without including secret values.

## Setup Commands

```bash
python skills/mochi-squad/scripts/setup.py --plan
python skills/mochi-squad/scripts/setup.py --install
python skills/mochi-squad/scripts/setup.py --verify
python skills/mochi-squad/scripts/setup.py --repair
```

Expected behavior:

- `--plan`: side-effect-free; reports intended file/profile/script changes and warnings.
- `--install`: creates missing runtime directories, config/state, copied scripts, and missing core profiles idempotently.
- `--verify`: side-effect-free readiness/doctor check for runtime files, core profiles, worker skill availability, and watcher script presence.
- `--repair`: conservative missing-file repair; does not overwrite existing SOUL/config files.

Core profiles:

```text
mochi-exec
mochi-review
```

Optional/future profile:

```text
mochi-research
```

Newly-created core profiles receive:

- minimal `SOUL.md` from `templates/profiles/<profile>/SOUL.md`;
- recommended Hermes-native `config.yaml` with `skills: [mochi-squad]` and role-appropriate `enabled_toolsets`;
- a local copy of the `mochi-squad` skill under the profile skill directory.

Existing profiles are audited and skipped. Setup must not silently overwrite existing SOUL or profile config files.

## Config vs State

```text
config = desired state
state  = observed/generated state
```

Example runtime config shape:

```yaml
kanban:
  db_path: auto

profiles:
  exec: mochi-exec
  review: mochi-review
  research: mochi-research  # optional/future

watchers:
  blocked:
    enabled: false
    schedule: "every 5m"
    notify_target: origin
    script: scripts/blocked-watchdog.py

virtual_office:
  enabled: false
  listen_host: 127.0.0.1
  port: 3000
  public_base_url: null
```

Example state facts:

```json
{
  "version": "0.1.0",
  "installed": true,
  "last_verified_at": "2026-01-01T00:00:00Z",
  "profiles": {
    "mochi-exec": {"status": "ok", "skill_installed": true},
    "mochi-review": {"status": "ok", "skill_installed": true}
  },
  "scripts": {
    "blocked-watchdog.py": {"installed": true, "sha256": "..."}
  },
  "blocked_watcher": {
    "cron_installed": false,
    "cron_job_id": null,
    "dedupe_state_path": "${HERMES_HOME}/mochi-squad/blocked-watchdog-state.json"
  }
}
```

These are examples only. They are not a v0.1 API contract.

## Blocked Watcher Boundary

The package ships `scripts/blocked-watchdog.py` as deterministic logic. It should be run by a Hermes cron with `no_agent=true` after explicit operator setup.

Behavior:

- no new blocked task/event: stdout is empty;
- new blocked event: stdout contains a concise notification payload;
- dedupe state is local runtime state, never committed to the package;
- script errors exit non-zero so broken watchdogs do not fail silently.

`setup.py` copies and checksums the watcher script, but it does not mutate Hermes cron jobs directly. Cron creation, delivery target, and notification permissions remain explicit/operator-approved setup actions.

## Readiness Levels

```text
skill_available
  The skill package is readable and can explain the workflow.

runtime_not_installed
  Required runtime files/profiles are missing.

runtime_warn
  Runtime exists but optional or repairable pieces are missing/stale.

runtime_ready
  Runtime state exists and cheap checks indicate configured components are installed.
```

## Agent Behavior

When an agent loads this skill:

1. Use the workflow guidance immediately.
2. If local runtime behavior is required, run `check_readiness.py` or `setup.py --verify`.
3. If readiness is missing/stale, show `setup.py --plan` before mutating files.
4. Do not auto-install unless the user explicitly asked for setup, install, verify, or repair.
5. After any explicit setup action, verify results before declaring success.
