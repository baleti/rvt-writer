#!/bin/bash
# finish_job.sh NAME YEAR SEED : writer file -> protocol -> Revit rooms finishing pass -> protocol on the finished file
cd ~/rvt-research/write-lab
N=$1; Y=$2; F=generated/stageb/${N}_${Y}.rte
pipeline/stageb_job.sh $N $Y $F $3 || exit 1
python3 tools/finish_rooms.py $Y $F generated/stageb/${N}_fin_${Y}.rte $F.json || exit 1
cp $F.json generated/stageb/${N}_fin_${Y}.rte.json
timeout 3300 python3 -u stageb_verify.py $Y generated/stageb/${N}_fin_${Y}.rte ${N}fin generated/stageb/${N}_fin_${Y}.rte.json | tail -12
