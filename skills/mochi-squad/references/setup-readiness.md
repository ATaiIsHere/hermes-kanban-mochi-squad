# Mochi Squad Setup and Readiness

Status: v0.1 draft for open-source packaging.

## Purpose

This document separates reusable skill content from local runtime installation state.

```text
skill package = reusable docs, templates, schemas, scripts
runtime install = local config, state, profiles, watchers, services
```

Loading the skill should give an agent workflow knowledge. It should not silently install dependencies, create profiles, create cron jobs, start services, rewrite config, or repair the host.

## Recommended Skill Package Layout

```text
skills/mochi-squad/
  SKILL.md
  references/
    orchestrator-guideline.md
    setup-readiness.md
```

Future package versions may add:

```text
skills/mochi-squad/
  templates/
    mochi-squad.config.yaml
  scripts/
    check_readiness.py
    setup.py
  references/
    config.schema.json
```

## Recommended Runtime Layout

Runtime files should live outside reusable skill files. A local install may use:

```text
${HERMES_HOME}/mochi/mochi-squad/
  config.yaml
  state.json
  logs/
  cache/
```

Definitions:

- `config.yaml`: desired local deployment config, usually copied from a template.
- `state.json`: observed install/runtime state updated by explicit setup, verify, repair, watcher, or service commands.
- `logs/`: runtime logs for watchers or optional services.
- `cache/`: disposable readiness or API cache data.

Do not store raw secrets, API tokens, OAuth credentials, private keys, personal data, local chat ids, or webhook URLs in committed files. Config may refer to secret locations or environment variable names without including secret values.

## Config vs State

```text
config = desired state
state  = observed state
```

Example config shape:

```yaml
profiles:
  plan: mochi-plan
  exec: mochi-exec
  review: mochi-review
  research: mochi-research

watchers:
  blocked:
    enabled: false
    schedule: "every 5m"
    notify_target: origin

virtual_office:
  enabled: false
```

Example state shape:

```json
{
  "version": "0.1.0",
  "installed": true,
  "last_verified_at": "2026-01-01T00:00:00Z",
  "readiness": "runtime_ready",
  "blocked_watcher": {
    "installed": false,
    "last_status": "not_configured"
  },
  "virtual_office": {
    "installed": false,
    "reason": "deferred"
  },
  "profiles": {
    "mochi-exec": {"exists": true},
    "mochi-review": {"exists": true}
  }
}
```

These are examples only. They are not a v0.1 API contract.

## Readiness Levels

A skill can be available while the runtime is missing.

Use these coarse readiness levels:

```text
skill_available
  The skill package is readable and can explain the workflow.

runtime_not_installed
  No runtime marker/state exists, or required install markers are missing.

runtime_ready
  Runtime state exists and cheap checks indicate configured components are installed.
```

Optional finer states may include:

```text
runtime_partial
runtime_stale
runtime_broken
```

## Lightweight Readiness Check

A future `scripts/check_readiness.py` should be cheap and side-effect-free.

It may check:

- whether runtime `state.json` exists;
- whether state version is compatible with the skill version;
- whether config exists or can be derived from a template;
- whether recorded profiles were previously verified;
- whether Virtual Office is intentionally disabled, missing, or installed.

It should not:

- install dependencies;
- create profiles;
- create cron jobs;
- start, stop, or restart services;
- rewrite config;
- run expensive database crawls or long service checks.

Suggested JSON output when runtime state is missing:

```json
{
  "ready": false,
  "readiness": "runtime_not_installed",
  "setup_needed": true,
  "missing": ["state.json not found"],
  "suggested_action": "run scripts/setup.py --install"
}
```

## Explicit Setup Commands

Full install, verify, and repair should be explicit operations:

```bash
python skills/mochi-squad/scripts/setup.py --install
python skills/mochi-squad/scripts/setup.py --verify
python skills/mochi-squad/scripts/setup.py --repair
```

Expected behavior:

- `--install`: create local runtime config/state and install selected components idempotently.
- `--verify`: perform complete checks and update observed state.
- `--repair`: fix missing or broken components where safe, otherwise report required user action.

All setup operations must be idempotent and safe to re-run. They must not commit generated state back into the reusable skill package.

## Agent Behavior

When an agent loads this skill:

1. Use the workflow guidance immediately.
2. If local runtime behavior is required, run or request the lightweight readiness check.
3. If readiness is `runtime_not_installed`, report that setup is needed.
4. Do not auto-install unless the user explicitly asked for setup, install, verify, or repair.
5. After any explicit setup action, verify results before declaring success.

## Open-Source Packaging Notes

For public-intended repositories:

- avoid user-specific names, local host paths, chat ids, channel ids, domains, and private profile names in committed defaults;
- use examples like `mochi-exec`, `mochi-review`, `origin`, and `${HERMES_HOME}`;
- include `.env.example` only when necessary, never real secrets;
- keep Hermes-native Kanban unmodified;
- document Mochi Squad as a convention layer over task graphs, comments, and handoffs;
- use selected-repository GitHub App installation access instead of broad personal PATs when automating repository writes.
