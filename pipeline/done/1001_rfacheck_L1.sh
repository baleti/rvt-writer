# timeout=1500
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/rfa_in/L1 ~/src/rvt-extract/out/rfa_chk/L1 > pipeline/logs/rfacheck_L1.log 2>&1
