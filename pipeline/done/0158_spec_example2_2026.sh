# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh spec_example2_2026 2026 generated/vp/2026_spec_example2.rte /home/user1/rvt-research/rosetta/2026_house_base.rte; python3 oracle_run.py views 2026 generated/vp/2026_spec_example2.rte; python3 check_views.py generated/vp/2026_spec_example2.rte.json ~/rvt-research/gt_views/2026_spec_example2.rte.views
