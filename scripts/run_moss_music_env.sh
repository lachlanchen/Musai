#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOSS_ENV="$ROOT_DIR/.conda/moss-music"
MOSS_SITE="$MOSS_ENV/lib/python3.12/site-packages"
MOSS_NVIDIA="$MOSS_SITE/nvidia"

if [[ ! -x "$MOSS_ENV/bin/python" ]]; then
  echo "Missing MOSS env: $MOSS_ENV" >&2
  echo "Run: bash scripts/install_quality_envs.sh moss-music" >&2
  exit 1
fi

export PYTHONNOUSERSITE=1
export LD_LIBRARY_PATH="$MOSS_ENV/lib:$MOSS_SITE/torch/lib:$MOSS_NVIDIA/cuda_runtime/lib:$MOSS_NVIDIA/cuda_nvrtc/lib:$MOSS_NVIDIA/npp/lib:$MOSS_NVIDIA/cublas/lib:$MOSS_NVIDIA/cudnn/lib:$MOSS_NVIDIA/cufft/lib:$MOSS_NVIDIA/cusolver/lib:$MOSS_NVIDIA/cusparse/lib:$MOSS_NVIDIA/cusparselt/lib:$MOSS_NVIDIA/nccl/lib:$MOSS_NVIDIA/nvjitlink/lib:$MOSS_NVIDIA/nvshmem/lib:$MOSS_NVIDIA/cufile/lib:$MOSS_NVIDIA/nvtx/lib:${LD_LIBRARY_PATH:-}"

if [[ $# -eq 0 ]]; then
  exec "$MOSS_ENV/bin/python"
fi

exec "$@"
