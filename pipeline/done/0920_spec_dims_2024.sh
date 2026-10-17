# timeout=3600
# vm
cd ~/rvt-research/write-lab
pipeline/stageb_job.sh dims_example 2024 generated/spec3/dims_example_2024.rte /home/user1/rvt-research/rosetta/2024_house_base.rte
mkdir -p generated/pick
python3 tools/pickwalls.py 2024 generated/spec3/dims_example_2024.rte generated/pick/2024_dimex.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2024_dimex.tsv
python3 tools/dimdump.py 2024 generated/spec3/dims_example_2024.rte generated/spec3/dims_2024.tsv | grep -a "^DIM" | grep -a "value=" | tail -2 | cut -c1-200
