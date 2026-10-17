# timeout=3600
# vm
cd ~/rvt-research/write-lab
python3 rvt_write.py finish 2026 generated/stageb/office7_2026.rte generated/fin/office7_openingsByRevit_2026.rte specs/fin_openings.json generated/stageb/office7_2026.rte.json 2>&1 | tail -3
python3 tools/pickwalls.py 2026 generated/fin/office7_openingsByRevit_2026.rte generated/pick/2026_office7openingsByRevit.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2026_office7openingsByRevit.tsv
