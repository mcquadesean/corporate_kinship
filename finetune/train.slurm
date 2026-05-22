#!/bin/bash
#SBATCH --job-name=ck_lora
#SBATCH --partition=gengpu
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=ck_lora_%j.log

set -e
cd "$SLURM_SUBMIT_DIR"

# activate the conda env created in setup_env.sh
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate ck_ft

python train_lora.py \
  --base Qwen/Qwen2.5-1.5B-Instruct \
  --train data/train.jsonl \
  --val data/val.jsonl \
  --out-dir runs/qwen2.5-1.5b-lora \
  --epochs 3

echo "training complete"
