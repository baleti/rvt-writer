# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh office8 2026 generated/stageb/office8_2026.rte /home/user1/rvt-research/rosetta/2026_house_base.rte; python3 oracle_run.py views 2026 generated/stageb/office8_2026.rte; python3 check_views.py generated/stageb/office8_2026.rte.json ~/rvt-research/gt_views/2026_office8_2026.rte.views
