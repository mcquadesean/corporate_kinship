import argparse

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def main():
    ap = argparse.ArgumentParser(description="Merge a LoRA adapter into its base model.")
    ap.add_argument("--base", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    model = AutoModelForCausalLM.from_pretrained(args.base, torch_dtype="bfloat16")
    model = PeftModel.from_pretrained(model, args.adapter)
    model = model.merge_and_unload()
    model.save_pretrained(args.out_dir)
    AutoTokenizer.from_pretrained(args.adapter).save_pretrained(args.out_dir)
    print("merged model ->", args.out_dir)


if __name__ == "__main__":
    main()
