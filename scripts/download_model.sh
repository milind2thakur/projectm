#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/models"
MODEL_NAME="projectm.gguf"

mkdir -p "$MODEL_DIR"

echo "Model download placeholder."
echo "Put your GGUF model at: $MODEL_DIR/$MODEL_NAME"
