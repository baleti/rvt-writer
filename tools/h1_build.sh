cd ~/rvt-research/write-lab; mkdir -p generated
for y in 2024 2026; do ./rvt-write scene specs/roofs5_$y.json generated/roofs5_$y.rte 2>&1 | tail -4; done
