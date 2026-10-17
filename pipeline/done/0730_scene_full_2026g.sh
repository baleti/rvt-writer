# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh full 2026 generated/full2/full_2026g.rte /home/user1/rvt-research/rosetta/2026_house_base.rte
mkdir -p generated/pick
python3 tools/pickwalls.py 2026 generated/full2/full_2026g.rte generated/pick/2026_full2g.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2026_full2g.tsv
