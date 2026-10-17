# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh house2 2026 generated/stageb/house2_2026.rte /home/user1/rvt-research/rosetta/2026_house_base.rte
mkdir -p generated/pick
python3 tools/pickwalls.py 2026 generated/stageb/house2_2026.rte generated/pick/2026_house2.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2026_house2.tsv
