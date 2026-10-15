#!/bin/bash
# rt.sh YEAR TAG LOCALFILE AUDIT SAVEAS : upload, run; restart Revit after any OPENFAIL; prints result line
Y=$1; T=$2; F=$3; A=${4:-false}; S=${5:-false}
cd ~/rvt-research/write-lab
B=$(basename $F)
./vmw.sh put $F C:/wl/$B >/dev/null
out=$(timeout 200 ./vmw.sh job $Y $T C:/wl/$B $A $S 2>&1 | grep -v '^$' | tr '\n' ' ')
echo "[$Y $T audit=$A] $out" | cut -c1-400
if echo "$out" | grep -qE "OPENFAIL|rror|Traceback"; then
  ./vmw.sh down $Y >/dev/null 2>&1; ./vmw.sh up $Y >/dev/null 2>&1; echo "(restarted Revit $Y)"
fi
