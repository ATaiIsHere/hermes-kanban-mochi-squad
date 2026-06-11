#!/usr/bin/env bash
set -euo pipefail
python -m unittest discover -s tests -v
python -m py_compile scripts/*.py
python scripts/validate_package.py
