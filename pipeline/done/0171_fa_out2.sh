# timeout=4000
# vm
cd ~/rvt-research/write-lab
python3 tools/finish_all.py 2026 generated/vp/2026_spec_example.rte generated/vp/2026_fa_out2.rte specs/finish_example.json generated/vp/2026_spec_example.rte.json && python3 tools/doordump.py 2026 generated/vp/2026_fa_out2.rte /home/user1/rvt-research/gt_views/2026_fa_out2.doors.tsv 303749,2307 && python3 oracle_run.py export 2026 generated/vp/2026_fa_out2.rte
