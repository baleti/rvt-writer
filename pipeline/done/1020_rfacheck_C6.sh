# timeout=1500
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/rfa_in/C6 ~/src/rvt-extract/out/rfa_chk/C6 > pipeline/logs/rfacheck_C6.log 2>&1
