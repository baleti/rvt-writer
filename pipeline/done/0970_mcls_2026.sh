# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh mcls 2026 generated/mcls/mcls_2026.rte /home/user1/rvt-research/rosetta/2026_house_base.rte
python3 tools/pickwalls.py 2026 generated/mcls/mcls_2026.rte generated/pick/mcls_2026.tsv | tail -1
python3 tools/pickcheck.py generated/pick/mcls_2026.tsv
