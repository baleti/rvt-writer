# timeout=1500
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/rfa_in/A0 ~/src/rvt-extract/out/rfa_chk/A0 > pipeline/logs/rfacheck_A0.log 2>&1
