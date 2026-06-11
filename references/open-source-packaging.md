# Open Source Packaging

Use this reference when preparing Mochi Squad for publication or external review.

## Package Shape

This repository is a single-skill package. The skill root is the repository root:

```text
SKILL.md
references/
templates/
scripts/
examples/
tests/
README.md
CHANGELOG.md
LICENSE
```

Do not reintroduce `skills/mochi-squad/` unless the repository is intentionally converted into a multi-skill collection.

## Public Safety

Committed defaults must not include:

- personal names or private project-specific routing;
- local host paths;
- platform/chat/channel IDs;
- OAuth tokens, private keys, installation tokens, PATs, or webhook URLs;
- generated cron IDs;
- runtime logs/cache/state;
- health data or private user content.

Use placeholders such as `${HERMES_HOME}`, `origin`, `mochi-exec`, and `mochi-review`.

## CI Expectations

At minimum, CI or the local CI entrypoint should run:

```bash
python -m unittest discover -s tests -v
python -m py_compile scripts/*.py
python scripts/validate_package.py
bash scripts/ci-local.sh
```

## Release Gate

Before merging or publishing:

- tests pass locally; GitHub Actions workflow installation requires repository workflow permission;
- package validation passes;
- private/local term scan passes;
- SKILL.md routes every active role-facing reference;
- setup is verified in an isolated Hermes home;
- reviewer confirms no runtime state or credentials are committed.
