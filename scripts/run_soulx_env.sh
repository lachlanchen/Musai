#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOULX_ENV="$ROOT_DIR/.conda/soulxsinger"
SOULX_REPO="$ROOT_DIR/third_party/SoulX-Singer"

if [[ ! -x "$SOULX_ENV/bin/python" ]]; then
  echo "Missing SoulX env: $SOULX_ENV" >&2
  echo "Run: bash scripts/install_quality_envs.sh soulx" >&2
  exit 1
fi

export PYTHONNOUSERSITE=1
export PYTHONPATH="$SOULX_REPO:${PYTHONPATH:-}"

if [[ $# -eq 0 ]]; then
  exec "$SOULX_ENV/bin/python"
fi

exec "$@"
