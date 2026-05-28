#!/bin/bash
set -e
[ -n "$1" ] && echo "$1" > ~/ids.txt
HTID=$(head -1 ~/ids.txt)
ENC=$(echo "$HTID" | sed 's/:/+/g; s|/|=|g')
echo "downloading $HTID"
htrc download -o /media/secure_volume/vols ~/ids.txt
echo "--- pages downloaded:"
find /media/secure_volume/vols -path "*$ENC*" -name "0*.txt" | wc -l
