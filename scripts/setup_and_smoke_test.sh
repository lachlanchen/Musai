#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="${MUSIA_ENV_NAME:-${MUSAI_ENV_NAME:-musia}}"
RUN_NAME="${MUSIA_SMOKE_RUN_NAME:-${MUSAI_SMOKE_RUN_NAME:-smoke-danny}}"
MAX_DURATION="${MUSIA_SMOKE_MAX_DURATION:-${MUSAI_SMOKE_MAX_DURATION:-45}}"
ASR_MODEL="${MUSIA_SMOKE_ASR_MODEL:-${MUSAI_SMOKE_ASR_MODEL:-tiny}}"
DEMUCS_DEVICE="${MUSIA_DEMUCS_DEVICE:-${MUSAI_DEMUCS_DEVICE:-}}"

cd "$ROOT_DIR"
export PYTHONNOUSERSITE=1

echo "==> Bootstrapping Musia core env: $ENV_NAME"
bash scripts/bootstrap_musia.sh --env "$ENV_NAME"

echo "==> Downloading open test song"
SONG_PATH="$(conda run -n "$ENV_NAME" python scripts/download_open_songs.py --id danny-boy-1917 | awk 'NF { line = $0 } END { print line }')"

echo "==> Running smoke pipeline"
CMD=(
  conda run -n "$ENV_NAME" python scripts/run_pipeline.py "$SONG_PATH"
  --run-name "$RUN_NAME"
  --max-duration "$MAX_DURATION"
  --asr-model "$ASR_MODEL"
)

if [[ -n "$DEMUCS_DEVICE" ]]; then
  CMD+=(--demucs-device "$DEMUCS_DEVICE")
fi

"${CMD[@]}"

cat <<EOF

Smoke test complete.

Report:
  data/runs/$RUN_NAME/REPORT.md

Artifacts:
  data/runs/$RUN_NAME/stems/bass.wav
  data/runs/$RUN_NAME/stems/drums.wav
  data/runs/$RUN_NAME/stems/vocals.wav
  data/runs/$RUN_NAME/stems/other.wav
  data/runs/$RUN_NAME/stems/instrumental.wav
  data/runs/$RUN_NAME/stems/human_sound.wav
  data/runs/$RUN_NAME/analysis/beats.csv
  data/runs/$RUN_NAME/analysis/chords.csv
  data/runs/$RUN_NAME/analysis/lyrics.txt
EOF
