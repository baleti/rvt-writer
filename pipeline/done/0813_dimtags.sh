# timeout=3000
# vm
cd ~/rvt-research/write-lab
for t in 0 1 2 3 4 5 7 8; do echo tag$t; python3 tools/open_test.py 2024 generated/stageb/dims1t${t}_2024.rte d1t$t | tail -1; done
