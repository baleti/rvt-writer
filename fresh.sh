#!/bin/bash
# fresh.sh YEAR TAG FILE AUDIT SAVEAS  -> restart Revit YEAR, then run the dump job
Y=$1; shift
cd ~/rvt-research/write-lab
for try in 1 2 3; do
  ./vmw.sh down $Y >/dev/null 2>&1
  P=$(./vmw.sh up $Y 2>&1 | sed -n 's/.*PORT=\([0-9]*\).*/\1/p')
  [ -n "$P" ] && break
done
echo $P > ports_$Y
./vmw.sh job $Y "$@" 2>&1 | grep -v '^$' | tail -4
