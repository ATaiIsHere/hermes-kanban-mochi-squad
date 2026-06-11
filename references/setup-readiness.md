# Mochi Squad Setup and Readiness

Setup separates reusable package files from local runtime state.

```text
package = docs, templates, scripts, examples, tests
runtime = local config, state, copied cron script, logs/cache, generated IDs
```

## Runtime Layout

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

Cron-compatible script copy:

```text
${HERMES_HOME}/scripts/mochi-squad-blocked-watchdog.py
```

Hermes cron scripts must live under `${HERMES_HOME}/scripts/`, so setup copies a cron-safe wrapper/copy there when cron install is explicitly requested.

## Commands

```bash
python scripts/setup.py --plan
python scripts/setup.py --install
python scripts/setup.py --verify
python scripts/setup.py --repair
python scripts/setup.py --install --install-cron
```

Behavior:

- `--plan`: side-effect-free intended changes and warnings.
- `--install`: create missing runtime files and core profiles; never overwrite existing SOUL/config.
- `--verify`: side-effect-free doctor check.
- `--repair`: conservative missing-file repair.
- `--install-cron`: explicit opt-in cron job creation/update in `${HERMES_HOME}/cron/jobs.json`.

## Core Profiles

```text
mochi-exec
mochi-review
```

New profiles receive minimal SOUL templates and recommended Hermes-native config. Existing profiles are audited only.

Recommended toolsets:

```text
mochi-exec:   file, terminal, kanban, skills
mochi-review: file, terminal, browser, kanban, skills
```

Review uses terminal/browser for verification, not implementation.

## Config vs State

Config records stable intent:

```yaml
kanban:
  db_path: auto

watchers:
  blocked:
    enabled: false
    schedule: "every 5m"
    notify_target: origin
    script: mochi-squad-blocked-watchdog.py

virtual_office:
  enabled: false
  listen_host: 127.0.0.1
  port: 3000
  public_base_url: null
```

State records generated/changing facts:

```json
{
  "version": "0.1.0",
  "profiles": {"mochi-exec": {"status": "ok"}},
  "scripts": {"blocked-watchdog.py": {"sha256": "..."}},
  "blocked_watcher": {"cron_installed": true, "cron_job_id": "..."}
}
```

## Approval Boundary

Scripts may create missing generated files when explicitly run. They must not configure DNS, Cloudflare, reverse proxies, credentials, production services, or public repositories.

Existing profile config changes require explicit approval outside the default install path. Setup reports proposed additions instead of editing.
