# timeout=18000
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh roofs3 2024 generated/stageb/roofs3_2024.rte /home/user1/rvt-research/rosetta/2024_house_base.rte
mkdir -p generated/pick
python3 tools/pickwalls.py 2024 generated/stageb/roofs3_2024.rte generated/pick/2024_roofs3.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2024_roofs3.tsv
