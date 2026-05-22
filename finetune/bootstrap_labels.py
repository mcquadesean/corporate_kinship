import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import extract_llm as el

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs):
        return x


def main():
    ap = argparse.ArgumentParser(
        description="Draft JSON affiliation labels for register entries using a "
                    "running LLM endpoint. Output is a starting point for hand-correction.")
    ap.add_argument("--in", dest="in_csv", required=True,
                    help="internal parser CSV with a raw_entry column")
    ap.add_argument("--out", required=True, help="output JSONL of draft labels")
    ap.add_argument("--server", default="http://localhost:8080")
    ap.add_argument("--model", default="local")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    with open(args.in_csv, newline="") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[:args.limit]

    written = 0
    with open(args.out, "w") as out:
        for row in tqdm(rows, desc="draft-labels"):
            entry = row.get("raw_entry", "").strip()
            if not entry:
                continue
            try:
                parsed = el.extract_json(el.call_model(args.server, args.model, entry))
            except Exception:
                parsed = None
            if not parsed or "affiliations" not in parsed:
                continue
            rec = {"entry": entry, "affiliations": parsed["affiliations"], "checked": False}
            out.write(json.dumps(rec) + "\n")
            written += 1

    print("wrote {} draft examples -> {}".format(written, args.out))
    print("NEXT: hand-correct each line, set \"checked\": true, then run prepare_data.py")


if __name__ == "__main__":
    main()
