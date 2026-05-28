#!/bin/bash
cd ~/corporate_kinship
HTID=$(head -1 ~/ids.txt) /opt/anaconda/bin/python - <<'PY'
import os, parse_register as pr
from pathlib import Path
htid = os.environ["HTID"]
enc = htid.replace(":", "+").replace("/", "=")
txt = sorted(p for p in Path("/media/secure_volume/vols").rglob("*.txt")
             if enc in str(p) and p.name[0].isdigit())
print("htid:", htid, "| total pages:", len(txt))
dense = [(i, sum(1 for l in p.read_text(errors="replace").splitlines()
                 if pr.looks_like_name_header(l.strip())))
         for i, p in enumerate(txt, 1)]
hits = [(i, n) for i, n in dense if n >= 8]
if hits:
    print("directors-dense index range:", hits[0][0], "to", hits[-1][0])
    print("first few (idx,count):", hits[:6])
else:
    print("no dense pages >=8; max per-page count was", max((n for _, n in dense), default=0))
PY
