# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh fport 2024 generated/fport/fport_2024.rte /home/user1/rvt-research/rosetta/2024_house_base.rte
python3 tools/pickwalls.py 2024 generated/fport/fport_2024.rte generated/pick/fport_2024.tsv | tail -1
python3 tools/pickcheck.py generated/pick/fport_2024.tsv
