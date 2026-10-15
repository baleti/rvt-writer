#!/bin/bash
# full_job.sh YEAR : full-coverage writer scene (specs/full_YEAR.json) -> full protocol + viewcheck -> Revit finishing pass -> open test + viewdump of the finished file
cd ~/rvt-research/write-lab
Y=$1; F=generated/full/full_$Y.rte; O=generated/full/full_fin_$Y.rte
pipeline/stageb_job.sh full $Y $F /home/user1/rvt-research/rosetta/${Y}_house_base.rte || exit 1
python3 oracle_run.py views $Y $F; python3 check_views.py $F.json ~/rvt-research/gt_views/${Y}_full_$Y.rte.views
python3 tools/finish_all.py $Y $F $O specs/full_finish_$Y.json $F.json || exit 1
cp $F.json $O.json
python3 tools/open_test.py $Y $O fullfin$Y
python3 oracle_run.py views $Y $O; grep -cP "^(OWNED|VIEWPORT)" ~/rvt-research/gt_views/${Y}_full_fin_$Y.rte.views
