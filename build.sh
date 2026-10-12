#!/usr/bin/env bash
# Build llama.cpp for macOS 12 Intel x64 with Hy-MT2 support

set -e

MODEL_PATH="${1:-$HOME/Hy-MT2-1.8B-Q4_K_M.gguf}"
BUILD_DIR="/tmp/llama.cpp-build-$(date +%s)"

echo "=== Hy-MT2 llama.cpp Builder ==="
echo "Model: $MODEL_PATH"
echo "Build dir: $BUILD_DIR"

# Check model exists
if [ ! -f "$MODEL_PATH" ]; then
    echo "ERROR: Model not found at $MODEL_PATH"
    echo "Download: curl -L \"https://huggingface.co/tencent/Hy-MT2-1.8B-GGUF/resolve/main/Hy-MT2-1.8B-Q4_K_M.gguf\" -o $MODEL_PATH"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
xcode-select -p >/dev/null 2>&1 || xcode-select --install

# Download CMake if not present
if ! command -v cmake &> /dev/null; then
    echo "Downloading CMake..."
    curl -sL "https://github.com/Kitware/CMake/releases/download/v3.29.3/cmake-3.29.3-macos-universal.tar.gz" -o /tmp/cmake.tar.gz
    tar -xzf /tmp/cmake.tar.gz -C /tmp
    export PATH="/tmp/cmake-3.29.3-macos-universal/CMake.app/Contents/bin:$PATH"
fi

# Clone llama.cpp (master branch for hunyuan-dense support)
echo "Cloning llama.cpp..."
git clone --depth 1 https://github.com/ggml-org/llama.cpp "$BUILD_DIR"
cd "$BUILD_DIR"

# Configure with Accelerate framework (native macOS BLAS, no OpenBLAS needed)
echo "Configuring CMake..."
cmake -B build \
  -DGGML_BLAS=OFF \
  -DGGML_METAL=OFF \
  -DCMAKE_OSX_DEPLOYMENT_TARGET=12.0 \
  -DCMAKE_OSX_ARCHITECTURES=x86_64 \
  -DCMAKE_C_FLAGS="-mmacosx-version-min=12.0" \
  -DCMAKE_CXX_FLAGS="-mmacosx-version-min=12.0" \
  -DLLAMA_BUILD_SERVER=ON \
  -DLLAMA_BUILD_CLI=ON

# Build
echo "Building (this takes 5-15 minutes)..."
cmake --build build -j$(sysctl -n hw.ncpu) --target llama-server llama-cli

# Verify
echo "Verifying binaries..."
./build/bin/llama-server -h >/dev/null && echo "✅ llama-server OK"
./build/bin/llama-cli -h >/dev/null && echo "✅ llama-cli OK"

# Copy to project directory
PROJECT_DIR="$(dirname "$0")"
mkdir -p "$PROJECT_DIR/bin"
cp build/bin/llama-server build/bin/llama-cli "$PROJECT_DIR/bin/"
echo "✅ Binaries copied to $PROJECT_DIR/bin/"

# Test with model
echo "Testing model loading..."
timeout 30 ./build/bin/llama-server -m "$MODEL_PATH" -c 8192 --port 18080 -ngl 0 &
sleep 8
if curl -s http://localhost:18080/health | grep -q "ok"; then
    echo "✅ Model loads successfully"
    pkill -f "llama-server.*18080"
else
    echo "⚠️  Model test failed (may need Q4_K_M instead of 1.25-bit)"
fi

echo ""
echo "=== Build Complete ==="
echo "Binaries: $PROJECT_DIR/bin/llama-server, $PROJECT_DIR/bin/llama-cli"
echo "Run server: ./run_server.sh $MODEL_PATH"
