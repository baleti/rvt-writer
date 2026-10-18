# timeout=1800
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/rfa_in/L2 ~/src/rvt-extract/out/rfa_chk/L2 > pipeline/logs/rfacheck_L2.log 2>&1
