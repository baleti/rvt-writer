# timeout=3000
# vm
cd ~/rvt-research/write-lab
for Y in 2024 2026; do for f in generated/full2/full_${Y}.rte generated/spec2/spec_example2_${Y}.rte; do b=$(basename $f .rte); python3 tools/pickwalls.py $Y $f generated/pick/${Y}_${b}_x.tsv | tail -1; python3 tools/pickcheck.py generated/pick/${Y}_${b}_x.tsv; done; done
