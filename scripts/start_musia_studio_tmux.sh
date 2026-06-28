#!/usr/bin/env bash
set -euo pipefail

SESSION="${MUSIA_STUDIO_SESSION:-${MUSAI_STUDIO_SESSION:-musia-studio}}"
PORT="${MUSIA_STUDIO_PORT:-${MUSAI_STUDIO_PORT:-8765}}"
HOST="${MUSIA_STUDIO_HOST:-${MUSAI_STUDIO_HOST:-127.0.0.1}}"
ENV_NAME="${MUSIA_ENV_NAME:-${MUSAI_ENV_NAME:-musia}}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/data/runs"
LOG_FILE="$LOG_DIR/musia-studio-server.log"
PORT_FILE="$LOG_DIR/musia-studio-server.port"

mkdir -p "$LOG_DIR"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  if [[ -f "$PORT_FILE" ]]; then
    PORT="$(cat "$PORT_FILE")"
  fi
  echo "Musia Studio already running in tmux session: $SESSION"
  echo "URL: http://$HOST:$PORT"
  exit 0
fi

if [[ -z "${MUSIA_STUDIO_PORT:-${MUSAI_STUDIO_PORT:-}}" ]]; then
  for candidate in $(seq "$PORT" 8785); do
    if ! ss -ltn | awk '{print $4}' | grep -Eq "(:|\\])${candidate}$"; then
      PORT="$candidate"
      break
    fi
  done
fi

printf '%s\n' "$PORT" > "$PORT_FILE"

for var_name in OPENAI_API_KEY OPENAI_MODEL DEEPSEEK_API_KEY DEEPSEEK_BASE_URL DEEPSEEK_MODEL HF_TOKEN MUSIA_CODEX_TIMEOUT MUSIA_CODEX_WORKER_TIMEOUT MUSAI_CODEX_TIMEOUT MUSAI_CODEX_WORKER_TIMEOUT; do
  if [[ -n "${!var_name:-}" ]]; then
    tmux set-environment -g "$var_name" "${!var_name}"
  fi
done

tmux new-session -d -s "$SESSION" \
  "cd '$ROOT_DIR' && PYTHONNOUSERSITE=1 conda run -n '$ENV_NAME' python scripts/musia_studio_web.py --host '$HOST' --port '$PORT' 2>&1 | tee '$LOG_FILE'"

echo "Started Musia Studio in tmux session: $SESSION"
echo "URL: http://$HOST:$PORT"
echo "Log: $LOG_FILE"
echo "Attach: tmux attach -t $SESSION"
