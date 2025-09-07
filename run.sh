#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
poetry install
poetry run uvicorn apps.backend.app:app --reload --port 8000
