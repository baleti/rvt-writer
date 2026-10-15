#!/bin/bash
cd ~/rvt-research/write-lab
python3 -u rosetta.py 2024 prof_curtain_mullion,prof_railing_handrail
for f in 2020/18_rst_basic_sample_project.rvt 2026/77_Construction-DefaultMetric.rte 2020/19_Commercial_Sample_Project.rvt 2020/20_Residential_Sample_Project.rvt 2026/75_Precast_Detailing-DefaultMetricCHS.rte 2024/70_Precast_Detailing-DefaultMetricCSY.rte; do
  y=${f%%/*}; b=$(basename $f); [ -s ~/rvt-research/gt_geom/${y}_$b.tsv ] && continue
  timeout 5400 python3 -u geomexport.py $y ~/rvt-research/corpus/$f --chunk 1000 --fam 5
done
python3 -u rosetta.py 2024 prof_curtain_mullion
