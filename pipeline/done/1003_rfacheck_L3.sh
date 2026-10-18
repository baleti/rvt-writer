# timeout=1800
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/rfa_in/L3 ~/src/rvt-extract/out/rfa_chk/L3 > pipeline/logs/rfacheck_L3.log 2>&1
