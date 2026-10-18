# timeout=3300
# vm
cd ~/rvt-research/write-lab
RFA_FLAT=1 python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/lift43 ~/src/rvt-extract/out/rfa_chk/lift43 > pipeline/logs/rfacheck_lift43.log 2>&1
