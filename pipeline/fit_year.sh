#!/bin/bash
# fit_year.sh YEAR : derive all fitted templates for a year from its rosetta files (offline)
cd ~/rvt-research/write-lab
export YEAR=$1
S=$([ $1 = 2024 ] && echo "" || echo "_$1")
run() { systemd-run --user --scope -q -p MemoryMax=8G -p MemorySwapMax=0 timeout 3000 "$@"; }
run python3 fitfloor.py | tail -3
run python3 fit_floor_z.py | tail -2
run python3 fit_columns.py | tail -4
run python3 fit_inst.py hosted_lv_base Windows files/winfit$S.json | tail -2
run python3 fit_inst.py hosted_lv_base Doors files/doorfit$S.json | tail -2
ls -la files/floorfit$S.json files/floorslope$S.json files/colfit$S.json
