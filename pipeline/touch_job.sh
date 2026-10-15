#!/bin/bash
# touch_job.sh NAME YEAR : writer file generated/stageb/NAME_YEAR.rte -> Revit touch pass (every wall regenerated: join data + the spatial pick key that writer-made walls lack,
#   without it Revit's 3D hover/ReferenceIntersector misses most writer walls) -> 3D pick check of every wall -> full protocol on the touched file
cd ~/rvt-research/write-lab
N=$1; Y=$2; F=generated/stageb/${N}_${Y}.rte; O=generated/stageb/${N}_t_${Y}.rte
python3 tools/finish_all.py $Y $F $O specs/fin_touch.json $F.json | tail -3 || exit 1
cp $F.json $O.json
mkdir -p generated/pick
python3 tools/pickwalls.py $Y $O generated/pick/${Y}_${N}_t.tsv | tail -1
python3 tools/pickcheck.py generated/pick/${Y}_${N}_t.tsv || exit 1
timeout 3300 python3 -u stageb_verify.py $Y $O ${N}t generated/stageb/${N}_t_${Y}.rte.json | tail -12
