#!/bin/bash
PAGES="$1"; YEAR="${2:-unknown}"
HTID=$(head -1 ~/ids.txt)
ENC=$(echo "$HTID" | sed 's/:/+/g; s|/|=|g')
VOLDIR=$(dirname "$(find /media/secure_volume/vols -path "*$ENC*" -name "0*.txt" | head -1)")
mkdir -p /media/secure_volume/out
cd ~/corporate_kinship
/opt/anaconda/bin/python parse_register.py "$VOLDIR" --htid "$HTID" --year "$YEAR" --pages "$PAGES" --out /media/secure_volume/out/${ENC}_${YEAR}.csv
