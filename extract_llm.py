import argparse
import csv
import json
import re
import urllib.request

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs):
        return x

SYSTEM = (
    "You are a precise data-extraction tool. You read one biographical entry from a "
    "business directory and output only JSON. Never invent information that is not "
    "present in the text."
)

USER_TEMPLATE = (
    "This is one entry from the Standard & Poor's Register of Directors and Executives. "
    "Extract every company affiliation the person holds.\n\n"
    "Entry:\n\"\"\"\n{entry}\n\"\"\"\n\n"
    "Return ONLY this JSON object:\n"
    '{{"affiliations":[{{"firm":"<company>","title":"<role(s) as written>",'
    '"city":"<business city or null>","state":"<business state or null>"}}]}}\n'
    "Rules:\n"
    "- One object per company.\n"
    "- title = the role(s) at that firm, e.g. \"Pres & Dir\", \"V-P, Secy & Dir\".\n"
    "- Use the business address for city/state, never the residence (Res:).\n"
    "- If a value is absent use null.\n"
    "- Do not output the person's name or birth data. JSON only, no commentary."
)

PERSON_FIELDS = [
    "ht_volume_id", "source_volume_year",
    "surname", "given_name", "middle_name", "suffix",
]
OUT_FIELDS = PERSON_FIELDS + ["firm", "title", "city", "state"]


def call_model(server, model, entry, timeout=120):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": USER_TEMPLATE.format(entry=entry)},
        ],
        "temperature": 0,
        "max_tokens": 400,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        server.rstrip("/") + "/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    return body["choices"][0]["message"]["content"]


def extract_json(text):
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--server", default="http://localhost:8080")
    ap.add_argument("--model", default="local")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    with open(args.in_csv, newline="") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[:args.limit]

    out_rows = []
    failures = 0
    for row in tqdm(rows, desc="llm"):
        entry = row.get("raw_entry", "")
        if not entry.strip():
            continue
        try:
            content = call_model(args.server, args.model, entry)
            parsed = extract_json(content)
        except Exception:
            parsed = None
        if not parsed or "affiliations" not in parsed:
            failures += 1
            continue
        base = {k: row.get(k, "") for k in PERSON_FIELDS}
        for aff in parsed["affiliations"]:
            if not isinstance(aff, dict):
                continue
            out = dict(base)
            out["firm"] = aff.get("firm") or ""
            out["title"] = aff.get("title") or ""
            out["city"] = aff.get("city") or ""
            out["state"] = aff.get("state") or ""
            out_rows.append(out)

    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)

    print("input persons:", len(rows))
    print("affiliation rows:", len(out_rows))
    print("parse failures:", failures)
    print("output:", args.out)


if __name__ == "__main__":
    main()
