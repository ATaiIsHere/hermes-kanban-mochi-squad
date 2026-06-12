# Changelog

## 0.2.0

### Added

- `references/change-spec-format.md`: Mochi Change Spec format with change-id, Routing Metadata, Intent, Decisions, Behavior Spec Deltas, Implementation Notes, Task Plan, Verification Plan, Handoff Rules, and Open Questions sections. Includes writing guidance, examples of good/bad requirements, and Kanban mapping rules.
- `setup.py --install` now copies minimal model config (`provider`, `default`, `base_url`, `context_length`, `fallback_providers`) from root HERMES_HOME config.yaml into newly-created profile configs.
- `setup.py --install` creates profile-local `.env` symlinks to root HERMES_HOME `.env` when it exists and the profile `.env` does not.
- `setup.py --install` runs post-install static verify and reports failures.
- `setup.py --verify` now checks profile model config, .env file presence (and symlink target validity), provider env key presence (OpenRouter, OpenAI, Anthropic), and cron enabled state.
- `setup.py --verify --live-smoke`: opt-in live Hermes smoke prompts for core profiles (costs tokens, requires `hermes` CLI).
- `setup.py --no-link-env` flag to disable .env symlink creation.
- `setup.py --repair` documented as alias for `--install`; docs guide to `--install` as the normal idempotent path.
- Orchestrator dispatch preflight guidelines (verify assignee, forced skills, parent links before dispatching).
- Orchestrator result monitoring guidelines (no-agent watcher cron, notification channel, or explicit dashboard check).
- Profile dispatch smoke test section in setup-readiness.md.
- Cron watchdog verification section in setup-readiness.md.
- Installing merged repo as active skill section in open-source-packaging.md.

### Changed

- Version bumped from 0.1.0 to 0.2.0.
- SKILL.md now routes `references/change-spec-format.md`.
- Exec/review/orchestrator guidelines now reference `references/change-spec-format.md`.
- `recommended_profile_config()` accepts optional `root_model` parameter.
- `verify()` readiness string now includes warning count instead of generic `runtime_warn`.
- `validate_package.py` checks `references/change-spec-format.md` as required and routed.

## 0.1.0

### Added

- Single-skill repository layout with `SKILL.md` at repo root.
- `SKILL.md` role router with explicit role/shared reference routing.
- Role guides for orchestrator, exec, review, and optional/future researcher roles.
- Shared Project graph, review fix loop, and PR handoff policies.
- Deterministic setup flow with `--plan`, `--install`, `--verify`, and `--repair`.
- Core profile bootstrapping/audit for `mochi-exec` and `mochi-review`.
- Runtime `state.yaml` tracking for profile audits, script checksums, and cron job IDs.
- Quiet `blocked-watchdog.py` script for no-agent cron usage.
- Package validation script and local CI entrypoint (`scripts/ci-local.sh`).
- User stories and acceptance criteria reference.

### Changed

- Removed nested `skills/mochi-squad/` package layout.
- Removed core `mochi-plan` and `mochi-research` profile templates.
- Review profile defaults include terminal and browser for real verification.
