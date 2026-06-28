#!/usr/bin/env bash
set -euo pipefail

ENV_NAME="${MUSAI_ENV_NAME:-musai}"

cd "$(dirname "$0")/.."

PYTHONNOUSERSITE=1 conda run -n "$ENV_NAME" \
  python scripts/run_localization_performance_pipeline.py "$@"
