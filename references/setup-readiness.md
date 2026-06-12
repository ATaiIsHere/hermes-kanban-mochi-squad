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

### Profile Dispatch Smoke Test

`setup.py --install` proves the files exist; it does not by itself prove a worker profile can spawn with a usable model/provider credential set in every deployment. After setup, verify the runtime path and the real Hermes profiles separately:

```bash
hermes profile list
hermes -p mochi-exec config path
hermes -p mochi-review config path
hermes -p mochi-exec chat -q 'Health check: reply only OK, do not use tools.' --quiet
hermes -p mochi-review chat -q 'Health check: reply only OK, do not use tools.' --quiet
```

If a newly-created profile reports that no provider/API key is configured, add the deployment's intended `model.provider` / `model.default` to that profile config and intentionally share credentials only through the deployment-approved mechanism (for example, a profile-local `.env` symlink to the shared Hermes `.env` when that is the local convention). Do not assume child profiles inherit the default profile's provider settings.

### Cron Watchdog Verification

When `--install-cron` is used, verify both the generated runtime state and the scheduler-visible job:

- readiness should report `runtime_ready` and no missing checks;
- the cron job should be enabled, `no_agent=true`, using `mochi-squad-blocked-watchdog.py`;
- trigger one run and confirm `last_status=ok`; quiet stdout is expected when there are no new blocked tasks.

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
  "version": "0.2.0",
  "profiles": {"mochi-exec": {"status": "ok"}},
  "scripts": {"blocked-watchdog.py": {"sha256": "..."}},
  "blocked_watcher": {"cron_installed": true, "cron_job_id": "..."}
}
```

## Approval Boundary

Scripts may create missing generated files when explicitly run. They must not configure DNS, Cloudflare, reverse proxies, credentials, production services, or public repositories.

Existing profile config changes require explicit approval outside the default install path. Setup reports proposed additions instead of editing.
