# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh dims_example 2024 generated/spec3/dims_example_2024.rte /home/user1/rvt-research/rosetta/2024_house_base.rte
python3 tools/dimdump.py 2024 generated/spec3/dims_example_2024.rte generated/spec3/dims_2024.tsv | grep -a "Diagonal" | cut -c1-230
