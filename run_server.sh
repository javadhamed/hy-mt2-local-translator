#!/usr/bin/env bash
# Run Hy-MT2 translation server

set -e

MODEL_PATH="${1:-$HOME/Hy-MT2-1.8B-Q4_K_M.gguf}"
PORT="${2:-8081}"
CTX="${3:-8192}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LLAMA_SERVER="$SCRIPT_DIR/bin/llama-server"

if [ ! -f "$LLAMA_SERVER" ]; then
    echo "ERROR: llama-server not found at $LLAMA_SERVER"
    echo "Run ./build.sh first"
    exit 1
fi

if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: Model not found at $MODEL_PATH"
    exit 1
fi

echo "=== Starting Hy-MT2 Translation Server ==="
echo "Model: $MODEL_PATH"
echo "Port: $PORT"
echo "Context: $CTX"
echo "Server binary: $LLAMA_SERVER"
echo ""

# Kill existing server on same port
pkill -f "llama-server.*--port $PORT" 2>/dev/null || true

# Start server
exec "$LLAMA_SERVER" \
  -m "$MODEL_PATH" \
  -c "$CTX" \
  --host 0.0.0.0 \
  --port "$PORT" \
  -ngl 0
