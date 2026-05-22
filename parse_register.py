import argparse
import csv
import re
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs):
        return x

RUNNING_HEADER_RE = re.compile(
    r"^(STANDARD\s*&?\s*POOR'?S|POOR'?S)\s+REGISTER", re.IGNORECASE
)
PAGE_NUMBER_RE = re.compile(r"^\d{1,5}$")
NAME_HEADER_RE = re.compile(r"^([A-Z][A-Z .,'’&-]*?),\s+([A-Z].*)$")
BIRTH_RE = re.compile(r"\(b\.\s*(\d{4})\s+([^)]*)\)")
SUFFIX_RE = re.compile(r"\b(Jr|Sr|II|III|IV)\b\.?", re.IGNORECASE)
RES_SPLIT_RE = re.compile(r"-\s*Res[:.]", re.IGNORECASE)


def is_page_header(line):
    return bool(PAGE_NUMBER_RE.match(line) or RUNNING_HEADER_RE.match(line))


def looks_like_name_header(line):
    m = NAME_HEADER_RE.match(line)
    if not m:
        return False
    surname = m.group(1)
    if not any(c.isalpha() for c in surname):
        return False
    return not any(c.islower() for c in surname)


def iter_record_blocks(lines):
    current = None
    for raw in lines:
        line = raw.strip()
        if not line or is_page_header(line):
            continue
        if looks_like_name_header(line):
            if current is not None:
                yield current
            current = [line]
        elif current is not None:
            current.append(line)
    if current is not None:
        yield current


def join_block(block):
    text = ""
    for line in block:
        line = line.strip()
        if not line:
            continue
        if text.endswith("-") and line[:1].islower():
            text = text[:-1] + line
        elif text:
            text = text + " " + line
        else:
            text = line
    return text


def split_name(header_text):
    surname, _, rest = header_text.partition(",")
    surname = surname.strip()
    given = re.split(r"[(\-]", rest, maxsplit=1)[0].strip()
    suffix = ""
    sm = SUFFIX_RE.search(given)
    if sm:
        suffix = sm.group(1)
        given = SUFFIX_RE.sub("", given).strip(" ,")
    parts = given.split()
    middle = ""
    given_first = given
    if len(parts) > 1:
        given_first = parts[0]
        middle = " ".join(parts[1:])
    return surname, given_first, middle, suffix


def parse_birth(text):
    m = BIRTH_RE.search(text)
    if not m:
        return "", ""
    year = m.group(1)
    place = m.group(2).strip()
    place = re.split(r"\s*-\s*|;", place)[0].strip(" ,")
    return year, place


def parse_record(block, htid, volume_year):
    text = join_block(block)
    header_text = block[0]
    surname, given, middle, suffix = split_name(header_text)
    birth_year, birth_place = parse_birth(text)
    return {
        "ht_volume_id": htid,
        "source_volume_year": volume_year,
        "surname": surname,
        "given_name": given,
        "middle_name": middle,
        "suffix": suffix,
        "birth_year": birth_year,
        "birth_place": birth_place,
        "raw_entry": text,
    }


def page_files(volume_dir):
    paths = sorted(Path(volume_dir).rglob("*.txt"))
    return [p for p in paths if p.name[0].isdigit()]


def select_pages(paths, page_range):
    if not page_range:
        return paths
    start, _, end = page_range.partition("-")
    start = int(start)
    end = int(end) if end else start
    return paths[start - 1:end]


def parse_volume(volume_dir, htid, volume_year, page_range=None):
    paths = select_pages(page_files(volume_dir), page_range)
    lines = []
    for path in paths:
        lines.extend(path.read_text(errors="replace").splitlines())
    records = []
    for block in tqdm(list(iter_record_blocks(lines)), desc="records"):
        records.append(parse_record(block, htid, volume_year))
    return records


FIELDS = [
    "ht_volume_id",
    "source_volume_year",
    "surname",
    "given_name",
    "middle_name",
    "suffix",
    "birth_year",
    "birth_place",
    "raw_entry",
]

EXPORT_FIELDS = [f for f in FIELDS if f != "raw_entry"]


def write_csv(records, out_path, fields):
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("volume_dir")
    ap.add_argument("--htid", required=True)
    ap.add_argument("--year", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--pages", default=None,
                    help="page-file range into the sorted list, e.g. 600-610")
    args = ap.parse_args()
    records = parse_volume(args.volume_dir, args.htid, args.year, args.pages)
    write_csv(records, args.out, FIELDS)
    export_path = re.sub(r"\.csv$", "", args.out) + "_export.csv"
    write_csv(records, export_path, EXPORT_FIELDS)
    print(f"parsed {len(records)} person records")
    print(f"  internal (with raw text): {args.out}")
    print(f"  export-safe (no raw text): {export_path}")


if __name__ == "__main__":
    main()
