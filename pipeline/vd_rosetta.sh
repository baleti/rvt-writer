#!/bin/bash
# viewdump on every view rosetta file of a year (skips existing outputs)
cd ~/rvt-research/write-lab
Y=$1
for f in ~/rvt-research/rosetta/${Y}_view_*_{base,var}.rte; do
  [ -f "$f" ] || continue; b=$(basename $f)
  [ -s ~/rvt-research/gt_views/${b}.views ] && continue
  python3 oracle_run.py views $Y $f
  mv ~/rvt-research/gt_views/${Y}_${b}.views ~/rvt-research/gt_views/${b}.views 2>/dev/null
done
