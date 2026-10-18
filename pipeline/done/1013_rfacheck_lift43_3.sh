# timeout=1500
# vm
cd ~/rvt-research/write-lab
RFA_FLAT=1 RFA_SLICE=90:120 python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/lift43 ~/src/rvt-extract/out/rfa_chk/lift43_3 > pipeline/logs/rfacheck_lift43_3.log 2>&1
