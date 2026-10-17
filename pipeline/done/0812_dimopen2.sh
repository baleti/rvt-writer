# timeout=3000
# vm
cd ~/rvt-research/write-lab
python3 tools/open_test.py 2024 generated/stageb/dims1noref_2024.rte d1nr | tail -1; python3 tools/open_test.py 2024 generated/stageb/dims1_2024.rte d1full | tail -1
