import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parse_register as pr

VOLS = "/media/secure_volume/vols"
OUT = "/media/secure_volume/out"


def enc(htid):
    return htid.replace(":", "+").replace("/", "=")


def main():
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(HERE, "bios_volumes.csv")) as f:
        rows = list(csv.DictReader(f))
    total = 0
    for r in rows:
        htid, year = r["htid"], r["year"]
        vol_dir = os.path.join(VOLS, enc(htid))
        if not os.path.isdir(vol_dir):
            print("MISSING DIR:", vol_dir)
            continue
        records = pr.parse_volume(vol_dir, htid, year)
        base = os.path.join(OUT, "{}_{}".format(enc(htid), year))
        pr.write_csv(records, base + ".csv", pr.RELEASE_FIELDS)
        pr.write_csv(records, base + "_noraw.csv", pr.NORAW_FIELDS)
        total += len(records)
        print("{} ({}): {} records".format(htid, year, len(records)))
    print("--- done: {} records across all volumes ---".format(total))


if __name__ == "__main__":
    main()
