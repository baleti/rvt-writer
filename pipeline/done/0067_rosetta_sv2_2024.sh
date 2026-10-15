# timeout=1200
# vm
cd ~/rvt-research/write-lab
python3 -u rosetta.py 2024 sheet_viewport2; grep -h . pipeline/logs/0067_rosetta_sv2_2024.sh.log | tail -3
