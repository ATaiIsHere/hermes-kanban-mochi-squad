# Mochi Change Spec Format

A Mochi Change Spec is the specification document for a repo-level change
in the Mochi Squad Kanban workflow. It is the bridge between Kanban task
metadata and deterministic implementation/review gates.

## Change ID

Every change has a stable **change-id**: a kebab-case identifier that serves
as the single cross-reference across Kanban, git branches, documentation,
PR descriptions, and project archives.

A change-id is **not** merely a subdirectory or folder name. It is the
durable key that:

- appears in the root Kanban task title or latest superseding comment;
- names the git branch (`improve-setup-readiness`);
- labels the PR title and body;
- identifies the change in CHANGELOG entries;
- links verification evidence back to the intended scope.

```
change-id: improve-setup-readiness
```

## Kanban-First Format

The spec lives in the root Kanban task body or (when too large for a single
task body) in the latest superseding comment on the root task. Child exec
and review tasks reference the root task and the relevant sections by name;
they do not copy the full spec.

### 1. Routing Metadata

Document the Kanban project structure:

```yaml
change-id: <unique-kebab-id>
project:   <root-task-id>
parent:    <parent-task-id-or-none>
exec:      <exec-task-id>
review:    <review-task-id>
repo:      <repo-path-or-url>
```

### 2. Intent

**Problem** — one or two sentences describing what is wrong or missing.

```
_Why_ does this change exist? Name the concrete user or system pain.
```

**Goal** — what the change should achieve after implementation.

```
_What_ success looks like. Prefer testable outcomes: "worker profiles
can dispatch without manual model config."
```

**Non-goals** — intentionally excluded scope so the exec worker does not
drift into adjacent work.

```
_What_ is explicitly _not_ in scope. Examples: "Does not redesign the
full setup flow." "Does not add new provider integrations."
```

### 3. Decisions

Record design choices and rejected alternatives with rationale. Each
decision should be self-contained so future workers or reviewers
understand why the path was taken.

```
decision: <short label>
context:  <why the decision was needed>
chosen:   <what was picked>
rejected: <what was considered and rejected, with reasoning>
```

### 4. Behavior Spec Deltas

The core of a Change Spec: a structured delta that says what must be
**ADDED**, **MODIFIED**, or **REMOVED** relative to the current state of
the repo or system.

Each delta line has the same shape:

```
STATUS: Requirement — <scenario>
```

Where `STATUS` is one of `ADDED`, `MODIFIED`, or `REMOVED`.

**Good requirements** are testable and specific:

```
ADDED: Profile model config — when `--install` creates a new profile,
its `config.yaml` must contain `model.provider` and `model.default`
from the root HERMES_HOME config.yaml if present.
```

```
MODIFIED: Verify checks profile credentials — `--verify` must report
`fail` when a core profile's config.yaml is missing `model.provider`
or `model.default`.
```

**Bad requirements** are vague or untestable:

```
BAD:  Make setup better.
BAD:  Improve verify output.
BAD:  Handle profiles correctly.
```

Each requirement should ideally be paired with a **Scenario** that
describes the observable conditions under which the requirement
holds:

```
Scenario: Fresh HERMES_HOME with root config that has
`model.provider: openrouter` and `model.default: deepseek/deepseek-chat`.
→ --install creates mochi-exec/config.yaml containing those two keys.
→ --install does not copy toolsets, agent, terminal, memory, gateway,
  or cron from root config.
→ --install mochi-exec/config.yaml does not contain any API keys.
```

```
Scenario: Existing profile with custom SOUL.md.
→ --install does not modify the SOUL.md content.
→ --install reports "skipped" for the existing file.
```

### 5. Implementation Notes

Free-form guidance for the exec worker. This can include:

- specific files to modify;
- functions to touch or leave alone;
- known design constraints or API contracts;
- order-of-operations recommendations.

### 6. Task Plan

A high-level ordered breakdown of the work, expressed as a sequence
of steps that the exec will follow. Each step maps to one or more
changed files.

```
1. Add references/change-spec-format.md.
2. Update SKILL.md to route the new reference.
3. Update exec/review guidelines to mention the spec.
...
```

This section is descriptive (what the root spec proposes), not
prescriptive (the exec may reorder or split as needed).

### 7. Verification Plan

A checklist of commands, tests, or manual checks that the exec must
run before handoff and the review must repeat or confirm.

Each verification line should be an actionable command or assert:

```
- python -m unittest discover -s tests -v
- python -m py_compile scripts/*.py
- python scripts/validate_package.py
- fresh-hermes-home install + verify passes
- second install does not duplicate cron jobs
- static verify catches missing model/env cases
```

### 8. Handoff Rules

Describe how the exec should hand off to review: what evidence to
include, what metadata shape to use, and how to block if needed.

```
handoff:
  summary: "<1-3 sentence summary of what was done>"
  metadata:
    changed_files: [...]
    tests_run: N
    tests_passed: N
  block_if:
    - tests do not pass
    - private keys/credentials found in modified files
    - existing user config would be overwritten
```

### 9. Open Questions

Any unresolved decisions or unknowns that were deferred. These are
addressed either by the exec during implementation or by the reviewer.

```
- Should we support per-profile model overrides beyond what the root config provides?
  Deferred to a future change.
```

---

## Kanban Mapping Rules

1. **Root task** (or its latest superseding comment) is the single source of truth (SSOT) for the spec. Exec and review tasks **reference** the root; they never copy the full spec into their own body.
2. **Exec task** body references `change-id`, root task id, and the relevant sections from the change-spec (e.g., "Implement sections 4, 6, 7").
3. **Review task** body references the same root and the spec sections the reviewer must verify against (especially Behavior Spec Deltas and Verification Plan).
4. When the spec is updated after the exec or review tasks are created, the orchestrator posts a superseding comment on the root task and re-creates affected child tasks.

---

## Writing Guidance Summary

| Section | Tone | Length | Key Question |
|---------|------|--------|--------------|
| Intent | Concise | 1-5 sentences each | Why does this exist? |
| Decisions | Matter-of-fact | 2-5 per decision | Why this way and not that? |
| Deltas | Precise | 1-N per requirement | What observably changes? |
| Implementation Notes | Helpful | As needed | Watch out for X. |
| Task Plan | Ordered | Steps 1-N | What order makes sense? |
| Verification Plan | Actionable | Checklist | How do we know it's done? |
| Handoff Rules | Structured | Template | What do I hand to review? |
| Open Questions | Honest | As needed | What don't we know yet? |