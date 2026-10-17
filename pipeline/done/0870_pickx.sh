# timeout=3000
# vm
cd ~/rvt-research/write-lab
for sc in roofs2 shift1; do python3 tools/pickwalls.py 2024 generated/stageb/${sc}_2024.rte generated/pick/2024_${sc}_x.tsv | tail -1; python3 tools/pickcheck.py generated/pick/2024_${sc}_x.tsv; done
