# Mochi Squad Profile Templates

These are minimal Hermes profile `SOUL.md` templates for a Mochi Squad runtime.

They are intentionally small. A profile template defines identity, hard boundaries, and which skill/reference to load. Detailed procedures live in `SKILL.md` and `references/*.md`.

## Core profiles

- `mochi-exec` — implementation worker.
- `mochi-review` — verification/review worker.

## Optional / future profiles

- `mochi-research` — optional research/spike worker, not installed by default in the core v0.1 setup.

There is no core `mochi-plan` template. Normal planning is owned by the conversation orchestrator and the root task as SSOT.

## Installation boundary

Do not overwrite existing Hermes profiles automatically. Setup tools may copy these templates only as part of an explicit install/repair action and should preserve existing user-edited profile files by default.
