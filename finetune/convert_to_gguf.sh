#!/bin/bash
# Merge LoRA, convert to GGUF, quantize. Produces a file to import into the capsule.
# Usage: bash convert_to_gguf.sh <adapter_dir> <output_name>
set -e

ADAPTER="${1:-runs/qwen2.5-1.5b-lora}"
NAME="${2:-ck-qwen2.5-1.5b}"
BASE="Qwen/Qwen2.5-1.5B-Instruct"
MERGED="runs/${NAME}-merged"

# 1. clone llama.cpp once for its conversion script
if [ ! -d llama.cpp ]; then
  git clone --depth 1 https://github.com/ggml-org/llama.cpp.git
  pip install -r llama.cpp/requirements.txt
fi

# 2. merge adapter into base
python merge_lora.py --base "$BASE" --adapter "$ADAPTER" --out-dir "$MERGED"

# 3. convert to GGUF (f16) then quantize to Q4_K_M
python llama.cpp/convert_hf_to_gguf.py "$MERGED" --outfile "runs/${NAME}-f16.gguf" --outtype f16

# llama-quantize comes from the prebuilt binary already staged in the capsule;
# if not on KLC, build it: cmake -B llama.cpp/build llama.cpp && cmake --build llama.cpp/build -j
QUANT=$(find . llama.cpp -name "llama-quantize" 2>/dev/null | head -1)
if [ -z "$QUANT" ]; then
  echo "building llama-quantize..."
  cmake -B llama.cpp/build llama.cpp >/dev/null && cmake --build llama.cpp/build -j --target llama-quantize >/dev/null
  QUANT=$(find llama.cpp/build -name "llama-quantize" | head -1)
fi
"$QUANT" "runs/${NAME}-f16.gguf" "runs/${NAME}-q4_k_m.gguf" Q4_K_M

echo "DONE -> runs/${NAME}-q4_k_m.gguf  (import this into the capsule ~/llm/models/)"
