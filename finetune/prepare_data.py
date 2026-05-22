import argparse
import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import extract_llm as el


def to_chat(rec):
    target = json.dumps({"affiliations": rec["affiliations"]}, ensure_ascii=False)
    return {"messages": [
        {"role": "system", "content": el.SYSTEM},
        {"role": "user", "content": el.USER_TEMPLATE.format(entry=rec["entry"])},
        {"role": "assistant", "content": target},
    ]}


def main():
    ap = argparse.ArgumentParser(
        description="Turn hand-corrected label JSONL into chat-format train/val splits. "
                    "Prompts match extract_llm exactly so training and inference align.")
    ap.add_argument("--in", dest="in_jsonl", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--val-frac", type=float, default=0.1)
    ap.add_argument("--require-checked", action="store_true",
                    help="only use lines with \"checked\": true")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    recs = []
    with open(args.in_jsonl) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if args.require_checked and not r.get("checked"):
                continue
            recs.append(r)

    random.Random(args.seed).shuffle(recs)
    n_val = max(1, int(len(recs) * args.val_frac)) if recs else 0
    val, train = recs[:n_val], recs[n_val:]

    os.makedirs(args.out_dir, exist_ok=True)
    for name, split in [("train", train), ("val", val)]:
        path = os.path.join(args.out_dir, name + ".jsonl")
        with open(path, "w") as out:
            for r in split:
                out.write(json.dumps(to_chat(r), ensure_ascii=False) + "\n")
        print("{}: {} examples -> {}".format(name, len(split), path))


if __name__ == "__main__":
    main()
