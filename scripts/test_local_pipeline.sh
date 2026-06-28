#!/usr/bin/env bash
set -euo pipefail
export PYTHONNOUSERSITE=1

ENV_NAME="${MUSIA_ENV_NAME:-${MUSAI_ENV_NAME:-musia}}"
SONG_PATH="$(conda run -n "$ENV_NAME" python scripts/download_open_songs.py --id danny-boy-1917 | awk 'NF { line = $0 } END { print line }')"
conda run -n "$ENV_NAME" python scripts/run_pipeline.py "$SONG_PATH" \
  --run-name smoke-danny \
  --max-duration 45 \
  --asr-model tiny

echo "Smoke test output: data/runs/smoke-danny/REPORT.md"
