# timeout=3000
# vm
cd ~/rvt-research/write-lab
for k in railing curtain; do PHASENAME="Phase 3" python3 tools/pickwalls.py 2024 ~/rvt-research/rosetta/2024_${k}_shift_base.rte generated/pick/2024_${k}_base3.tsv | tail -1; done
