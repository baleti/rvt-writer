#!/bin/bash
# vj.sh YEAR TAG LOCALFILE [audit] : upload, open with audit, dump classes+geometry; restarts Revit after failure
Y=$1; T=$2; F=$3; A=${4:-false}; cd ~/rvt-research/write-lab
if [ "${FRESH:-1}" = 1 ]; then ./vmw.sh down $Y >/dev/null 2>&1; P0=$(./vmw.sh up $Y 2>&1 | sed -n 's/.*PORT=\([0-9]*\).*/\1/p'); echo $P0 > ports_$Y; fi
B=$(basename $F); ./vmw.sh put $F C:/wl/$B >/dev/null
sed "s#__FILE__#C:/wl/$B#;s#__TAG__#$T#;s#__AUDIT__#$A#" jobs/verify_lines.cs > /tmp/claude-1000/vj_$T.cs
./vmw.sh put /tmp/claude-1000/vj_$T.cs C:/wl/job_$T.cs >/dev/null
echo "[$Y $T] $out"
if echo "$out" | grep -qE "OPENFAIL|Traceback|rror"; then ./vmw.sh down $Y >/dev/null 2>&1; P=$(./vmw.sh up $Y 2>&1 | sed -n 's/.*PORT=\([0-9]*\).*/\1/p'); echo $P > ports_$Y; echo "(restarted $Y on $P)"; else ./vmw.sh get C:/wl/out/${T}_geom.txt out/${T}_geom.txt 2>/dev/null; fi
