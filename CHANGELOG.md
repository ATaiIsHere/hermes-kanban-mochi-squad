# Changelog

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
