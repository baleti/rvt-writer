# timeout=3600
# vm
cd ~/rvt-research/write-lab
timeout 3300 python3 -u stageb_verify.py 2024 generated/dimfin/dimfin_2024.rte dimfin generated/dimfin/dimfin_2024.rte.json | tail -30
python3 tools/pickwalls.py 2024 generated/dimfin/dimfin_2024.rte generated/pick/2024_dimfin.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2024_dimfin.tsv
