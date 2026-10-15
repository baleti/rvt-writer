# timeout=3000
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh anno1 2024 generated/stageb/anno1_2024.rte /home/user1/rvt-research/rosetta/2024_house_base.rte; python3 oracle_run.py views 2024 generated/stageb/anno1_2024.rte; python3 check_views.py generated/stageb/anno1_2024.rte.json ~/rvt-research/gt_views/2024_anno1_2024.rte.views
