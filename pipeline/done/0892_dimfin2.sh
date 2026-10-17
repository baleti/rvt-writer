# timeout=3600
# vm
cd ~/rvt-research/write-lab
for Y in 2024 2026; do timeout 3300 python3 -u stageb_verify.py $Y generated/dimfin/dimfin2_$Y.rte dimfin2 generated/dimfin/dimfin2_$Y.rte.json | grep -a "API audit\|UI ok\|CHECK\|PASS\|FAIL"; python3 tools/dimdump.py $Y generated/dimfin/dimfin2_$Y.rte generated/dimfin/dims2_$Y.tsv | grep -a "value=" | grep -a "Diagonal\|refs=30" ; done
