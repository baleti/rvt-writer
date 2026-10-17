# timeout=3000
# vm
cd ~/rvt-research/write-lab
for v in refp val origin old gline wit; do echo $v; python3 tools/open_test.py 2024 generated/stageb/dims1o${v}_2024.rte d1o$v | tail -1; done
