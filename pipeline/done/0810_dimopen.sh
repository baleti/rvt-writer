# timeout=3000
# vm
cd ~/rvt-research/write-lab
for v in raw noref; do python3 tools/open_test.py 2024 generated/stageb/dims1${v}_2024.rte d1$v | tail -1; done; python3 tools/open_test.py 2024 generated/stageb/dims1_2024.rte d1full | tail -1
