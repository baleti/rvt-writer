# timeout=3000
# vm
cd ~/rvt-research/write-lab
python3 tools/open_test.py 2024 generated/dimfin/dimfin_2024.rte dimfin | tail -1
python3 tools/dimdump.py 2024 generated/dimfin/dimfin_2024.rte generated/dimfin/dims.tsv | tail -5
