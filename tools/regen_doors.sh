#!/bin/bash
# tools/regen_doors.sh : rebuild every delivered scene with writer doors after the door item-outline fix (2026-10-15) and queue its protocol
cd ~/rvt-research/write-lab
R=~/rvt-research/rosetta; run(){ systemd-run --user --scope -q -p MemoryMax=3G -p MemorySwapMax=0 nice -n 19 timeout 900 "$@"; }
n=150
for sy in house_lv:2024 house1:2024 house2:2024 types1:2024 house_lv:2026; do
  sc=${sy%%:*}; Y=${sy##*:}; f=generated/stageb/${sc}_${Y}.rte
  run python3 scenes.py $sc $f $Y | tail -1
  pipeline/enqueue.sh 0${n}_${sc}_$Y 3600 "pipeline/stageb_job.sh $sc $Y $f $R/${Y}_house_base.rte"; n=$((n+1))
done
for Y in 2024 2026; do
  run python3 scenes.py fitout1 generated/stageb/fitout1_$Y.rte $Y | tail -1
  pipeline/enqueue.sh 0${n}_fitout1_fin_$Y 5400 "pipeline/finish_job.sh fitout1 $Y $R/${Y}_house_base.rte"; n=$((n+1))
done
run python3 rvt_write.py scene specs/example_2026.json generated/vp/2026_spec_example.rte | tail -1
pipeline/enqueue.sh 0${n}_spec_example_2026 3600 "pipeline/stageb_job.sh spec_example_2026 2026 generated/vp/2026_spec_example.rte $R/2026_house_base.rte; python3 oracle_run.py views 2026 generated/vp/2026_spec_example.rte; python3 check_views.py generated/vp/2026_spec_example.rte.json ~/rvt-research/gt_views/2026_spec_example.rte.views"; n=$((n+1))
python3 rvt_write.py example > specs/example_full_2026.json
run python3 rvt_write.py scene specs/example_full_2026.json generated/vp/2026_spec_example2.rte | tail -1
pipeline/enqueue.sh 0${n}_spec_example2_2026 3600 "pipeline/stageb_job.sh spec_example2_2026 2026 generated/vp/2026_spec_example2.rte $R/2026_house_base.rte; python3 oracle_run.py views 2026 generated/vp/2026_spec_example2.rte; python3 check_views.py generated/vp/2026_spec_example2.rte.json ~/rvt-research/gt_views/2026_spec_example2.rte.views"; n=$((n+1))
for Y in 2024 2026; do run python3 rvt_write.py scene specs/full_$Y.json generated/full/full_$Y.rte | tail -1; pipeline/enqueue.sh 0${n}_full_$Y 7200 "pipeline/full_job.sh $Y"; n=$((n+1)); done
