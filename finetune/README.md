# Fine-tuning a small extractor

Goal: a small open model that turns a register entry into affiliation JSON, faster and
more accurate than the off-the-shelf 3B, trained on **public-domain (pre-1929)** text so
it can be done on a KLC GPU outside the capsule. Only the trained weights go into the
capsule; in-copyright text never leaves it.

Prompts here are imported from `../extract_llm.py`, so training and capsule inference use
the identical prompt.

## Steps

```
# 0. one-time env (KLC login node)
bash setup_env.sh && conda activate ck_ft

# 1. draft labels from a PUBLIC-DOMAIN year's parser output (raw_entry CSV)
#    (run wherever an LLM endpoint is up; output is a starting point only)
python bootstrap_labels.py --in pd_year_internal.csv --out labels.jsonl --server http://localhost:8080

# 2. HAND-CORRECT labels.jsonl  <-- the step that decides quality.
#    Fix firm/title/city/state, set "checked": true on each good line. Aim ~300-500.

# 3. build chat-format splits (prompts match inference exactly)
python prepare_data.py --in labels.jsonl --out-dir data --require-checked

# 4. LoRA fine-tune on an A100 (~30-60 min for 1.5B)
sbatch train.slurm        # or: python train_lora.py --train data/train.jsonl --val data/val.jsonl --out-dir runs/...

# 5. merge + convert to a quantized GGUF
bash convert_to_gguf.sh runs/qwen2.5-1.5b-lora ck-qwen2.5-1.5b

# 6. import runs/ck-qwen2.5-1.5b-q4_k_m.gguf into the capsule (~/llm/models/) in
#    MAINTENANCE mode, then serve + run extract_llm.py against it in SECURE mode.
```

Base model is `Qwen/Qwen2.5-1.5B-Instruct` by default; drop to `-0.5B` for faster capsule
inference if accuracy holds, or raise if needed (GPU is not the bottleneck).
