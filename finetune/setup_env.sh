#!/bin/bash
# One-time setup of the KLC conda env for fine-tuning. Run on a login node.
set -e

CONDA_SH="${CONDA_SH:-/software/miniconda3/4.12.0/etc/profile.d/conda.sh}"
source "$CONDA_SH"
conda create -y -n ck_ft python=3.10
conda activate ck_ft

pip install --upgrade pip
pip install "torch" --index-url https://download.pytorch.org/whl/cu121
pip install "transformers>=4.45" "trl>=0.12" "peft>=0.13" "datasets>=3.0" \
            "accelerate>=1.0" sentencepiece protobuf

echo "env ck_ft ready. activate with: conda activate ck_ft"
