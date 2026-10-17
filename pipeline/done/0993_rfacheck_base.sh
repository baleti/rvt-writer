# timeout=1500
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/rfa_in/base ~/src/rvt-extract/out/rfa_chk/base > pipeline/logs/rfacheck_base.log 2>&1
