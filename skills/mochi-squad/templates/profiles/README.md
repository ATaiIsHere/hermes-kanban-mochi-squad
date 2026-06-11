# Mochi Squad Profile Templates

These are minimal Hermes profile `SOUL.md` templates for a Mochi Squad runtime.

They are intentionally small. A profile template defines identity, hard boundaries, and which skill/reference to load. Detailed procedures live in `SKILL.md` and `references/*.md`.

## Core profiles

- `mochi-exec` — implementation worker.
- `mochi-review` — verification/review worker.

## Optional profiles

- `mochi-research` — optional research/spike worker.
- `mochi-plan` — optional fallback planning worker. The normal planning path is the conversation orchestrator plus the root task as SSOT; use `mochi-plan` only when an installation explicitly wants dispatched planning work.

## Installation boundary

Do not overwrite existing Hermes profiles automatically. Setup tools may copy these templates only after an explicit install/repair action and should preserve existing user-edited profile files by default.
