# timeout=1500
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/rfa_in/A2 ~/src/rvt-extract/out/rfa_chk/A2 > pipeline/logs/rfacheck_A2.log 2>&1
