# Changelog

All notable changes to this project will be documented in this file.

The format follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses semantic versioning once releases are tagged.

## [0.1.0] - Unreleased

### Added

- Initial skill-only Mochi Squad package for Hermes Kanban workflows.
- Project convention: root task plus descendants, with state derived from the native task graph.
- Orchestrator guidance for planning, execution, review, and recovery task chains.
- Setup/readiness guidance that separates reusable skill documentation from local runtime config and state.
- Blocked recovery guidance using exec rerun/resume-context and review fix insertion before the same review gate.
- Guard-safe PR handoff policy for retryable Kanban comments.

### Deferred

- Virtual Office server, UI, routes, and API response shapes.
- Hermes Kanban schema changes, custom task metadata, and dispatcher changes.
- Automated runtime installers, service restarts, and bundled credentials.
