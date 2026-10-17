# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh dims_example 2026 generated/spec3/dims_example_2026.rte /home/user1/rvt-research/rosetta/2026_house_base.rte
python3 tools/dimdump.py 2026 generated/spec3/dims_example_2026.rte generated/spec3/dims_2026.tsv | grep -a "Diagonal" | cut -c1-230
