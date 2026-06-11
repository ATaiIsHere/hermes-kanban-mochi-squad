---
name: mochi-squad
description: Role-routed workflow package for project-oriented multi-agent work on top of native Hermes Kanban.
version: 0.1.0
author: Mochi Squad contributors
license: MIT
metadata:
  hermes:
    tags: [kanban, multi-agent, orchestration, workflow, review, recovery]
    related_skills: [kanban-worker]
---

# Mochi Squad

Mochi Squad is a convention layer over native Hermes Kanban. It does not add Kanban schema fields, run a daemon, or replace Hermes scheduling. The package gives agents a shared Project model, role routing, setup scripts, and recovery rules.

## Load Order / Role Routing

Every profile that loads this skill must first identify its role from the active profile name, task body, or explicit instruction, then read the matching role guide before doing work.

```text
orchestrator / planner / coordinator -> references/roles/orchestrator-guideline.md
mochi-exec / implementation worker    -> references/roles/exec-guideline.md
mochi-review / reviewer / verifier    -> references/roles/review-guideline.md
research / spike worker               -> references/roles/researcher-guideline.md  (optional/future)
```

Shared references are loaded only when relevant:

```text
Project graph / status derivation -> references/shared/project-graph-conventions.md
Review needs_fix / rerun loops    -> references/shared/review-fix-loop.md
Retryable PR handoff              -> references/shared/pr-handoff-guard-policy.md
Setup / runtime / doctor          -> references/setup-readiness.md
Public package safety             -> references/open-source-packaging.md
User stories / acceptance         -> references/user-stories.md
```

If a role-facing file is not routed here, it is not active guidance for workers.

## Shared Principles

1. A Project is `root task + all descendants` via native Hermes Kanban links.
2. The root task is the specification source of truth.
3. Child tasks reference root scenarios instead of copying the whole spec.
4. Implementation and review are separate gates.
5. Review verifies and records evidence; it does not implement fixes.
6. Normal exec blocks rerun the same exec task with resume context.
7. Normal review `needs_fix` inserts a scoped fix before the same review gate.
8. Runtime state, cron IDs, logs, credentials, and local platform targets stay out of the package.

## Setup Boundary

The package ships deterministic scripts:

```bash
python scripts/setup.py --plan
python scripts/setup.py --install
python scripts/setup.py --verify
python scripts/setup.py --repair
```

These scripts can create/audit the local Mochi runtime and core worker profiles when explicitly run. Loading this skill alone must not install profiles, cron jobs, services, credentials, DNS, tunnels, or reverse proxies.

## High-Risk Warnings

- Do not mark failed or blocked work `done` merely to release dependencies.
- Do not create custom Kanban schema fields for Projects.
- Do not silently overwrite existing profile `SOUL.md` or `config.yaml`.
- Do not commit runtime state, private paths, chat IDs, tokens, keys, logs, or generated cron IDs.
- Do not treat examples/tests as worker runtime instructions.

## Verification Checklist

- [ ] Role is identified and the matching role guide was read.
- [ ] Project state can be derived from native task graph/status only.
- [ ] Setup changes were made only by explicit setup commands.
- [ ] Review evidence is produced by real checks, not guesses.
- [ ] Package paths are rooted at this single-skill repo root, not nested under `skills/mochi-squad/`.
