# timeout=3600
# vm
cd ~/rvt-research/write-lab
python3 rvt_write.py finish 2024 generated/stageb/house1_2024.rte generated/fin/house1_openingsByRevit_2024.rte specs/fin_openings.json generated/stageb/house1_2024.rte.json 2>&1 | tail -3
python3 tools/pickwalls.py 2024 generated/fin/house1_openingsByRevit_2024.rte generated/pick/2024_house1obr.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2024_house1obr.tsv
