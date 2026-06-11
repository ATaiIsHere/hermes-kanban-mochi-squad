# Hermes Kanban Mochi Squad

Mochi Squad is a single-skill workflow package for modeling project-oriented, multi-agent work on top of native Hermes Kanban.

Version `0.1.0` ships:

- `SKILL.md` as the compact role router/index.
- Role guides under `references/roles/`.
- Shared policies under `references/shared/`.
- Deterministic setup/readiness/watchdog scripts under `scripts/`.
- Minimal core profile templates for `mochi-exec` and `mochi-review`.
- Examples and tests for maintainers and human adopters.

It is not a Kanban schema fork, daemon, server, Virtual Office API, credential manager, DNS/tunnel/proxy configurator, or production deployment tool.

## Repository Layout

```text
SKILL.md
references/
  roles/
    orchestrator-guideline.md
    exec-guideline.md
    review-guideline.md
    researcher-guideline.md
  shared/
    project-graph-conventions.md
    review-fix-loop.md
    pr-handoff-guard-policy.md
  setup-readiness.md
  open-source-packaging.md
  user-stories.md
templates/
  mochi-squad.config.yaml
  profiles/
    mochi-exec/SOUL.md
    mochi-review/SOUL.md
scripts/
  setup.py
  check_readiness.py
  blocked-watchdog.py
  validate_package.py
examples/
tests/
```

This is intentionally a single-skill repository. Do not nest the package under `skills/mochi-squad/` unless the repository is converted into a multi-skill collection.

## Project Model

```text
Project = root task + all descendants
```

Project state is derived from native Hermes Kanban task status and links. See `references/shared/project-graph-conventions.md`.

## Standard Workflow

```text
root/spec -> exec -> review
```

Blocked recovery:

```text
exec block   -> resume-context -> same exec rerun
review fail  -> scoped fix -> same review gate rerun
```

See `references/shared/review-fix-loop.md`.

## Setup

The package can be used as documentation only, but local runtime setup is available through explicit deterministic commands:

```bash
python scripts/setup.py --plan
python scripts/setup.py --install
python scripts/setup.py --verify
python scripts/setup.py --repair
```

Cron installation is explicit opt-in:

```bash
python scripts/setup.py --install --install-cron
```

Setup creates missing runtime files under `${HERMES_HOME}/mochi-squad/`, creates missing core profiles, installs the package into worker profile skill directories, writes recommended config only for newly-created profiles, audits existing profiles, and records generated facts in `state.yaml`.

## Verification

```bash
python -m unittest discover -s tests -v
python -m py_compile scripts/*.py
python scripts/validate_package.py
bash scripts/ci-local.sh
```

## Public Safety

Never commit runtime state, generated cron IDs, local chat/platform IDs, private paths, tokens, keys, credentials, logs, or user data. See `references/open-source-packaging.md`.
