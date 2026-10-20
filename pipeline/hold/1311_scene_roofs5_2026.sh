# timeout=18000
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh roofs5 2026 generated/stageb/roofs5_2026.rte /home/user1/rvt-research/rosetta/2026_house_base.rte
mkdir -p generated/pick
python3 tools/pickwalls.py 2026 generated/stageb/roofs5_2026.rte generated/pick/2026_roofs5.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2026_roofs5.tsv
