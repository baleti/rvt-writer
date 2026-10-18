# timeout=1500
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/rfa_in/A3 ~/src/rvt-extract/out/rfa_chk/A3 > pipeline/logs/rfacheck_A3.log 2>&1
