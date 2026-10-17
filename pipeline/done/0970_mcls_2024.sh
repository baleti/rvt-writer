# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh mcls 2024 generated/mcls/mcls_2024.rte /home/user1/rvt-research/rosetta/2024_house_base.rte
python3 tools/pickwalls.py 2024 generated/mcls/mcls_2024.rte generated/pick/mcls_2024.tsv | tail -1
python3 tools/pickcheck.py generated/pick/mcls_2024.tsv
