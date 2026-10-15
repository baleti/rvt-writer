#!/bin/bash
# enq_scenes.sh YEAR scene... : build each scene for YEAR, vcheck, enqueue the full protocol
cd ~/rvt-research/write-lab
Y=$1; shift
SEED=~/rvt-research/rosetta/${Y}_house_base.rte
i=60
for sc in "$@"; do
  f=generated/stageb/${sc}_${Y}.rte
  [ -s $f.json ] || systemd-run --user --scope -q -p MemoryMax=10G -p MemorySwapMax=0 timeout 1200 python3 scenes.py $sc $f $Y > /dev/null 2>&1
  r=$(systemd-run --user --scope -q -p MemoryMax=5G -p MemorySwapMax=0 timeout 900 python3 vcheck.py $f --seed $SEED --manifest $f.json 2>&1 | tail -1)
  echo "$sc $Y vcheck: $r"
  case "$r" in *"PASS 0 errors"*) pipeline/enqueue.sh 00${i}_${sc}_$Y 3600 "pipeline/stageb_job.sh $sc $Y $f $SEED";; esac
  i=$((i+1))
done
