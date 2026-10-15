#!/bin/bash
# stageb_job.sh NAME YEAR FILE SEED : offline vcheck + full Revit protocol (queue as a job)
cd ~/rvt-research/write-lab
systemd-run --user --scope -q -p MemoryMax=5G -p MemorySwapMax=0 timeout 900 python3 vcheck.py $3 --seed $4 --manifest $3.json | tail -2 || exit 1
timeout 3300 python3 -u stageb_verify.py $2 $3 $1 $3.json | tail -40
