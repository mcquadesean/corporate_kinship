#!/bin/bash
# Segment all bios volumes listed in bios_volumes.csv.
# Run inside the capsule (SECURE mode), after volumes are in /media/secure_volume/vols.
set -u

PY=/opt/anaconda/bin/python
REPO="$(cd "$(dirname "$0")" && pwd)"
VOLS=/media/secure_volume/vols
OUT=/media/secure_volume/out
mkdir -p "$OUT"
cd "$REPO"

ok=0; miss=0; skip=0
while IFS=, read -r htid year type desc rights; do
    [ -z "$htid" ] && continue
    enc=$(echo "$htid" | sed 's/:/+/g; s|/|=|g')
    dir="$VOLS/$enc"
    out="$OUT/${enc}_${year}.csv"
    if [ ! -d "$dir" ]; then
        echo "MISSING DIR: $htid ($year) -> $dir"; miss=$((miss+1)); continue
    fi
    if [ -s "$out" ]; then
        echo "SKIP (done): $htid ($year)"; skip=$((skip+1)); continue
    fi
    echo "=== $htid ($year, $type) ==="
    "$PY" parse_register.py "$dir" --htid "$htid" --year "$year" --out "$out"
    ok=$((ok+1))
done < <(tail -n +2 bios_volumes.csv)

echo
echo "parsed: $ok | skipped(existing): $skip | missing dirs: $miss"
echo "outputs in $OUT (one <enc>_<year>.csv with raw_entry + a _noraw.csv each)"
