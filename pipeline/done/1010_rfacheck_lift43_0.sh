# timeout=1500
# vm
cd ~/rvt-research/write-lab
RFA_FLAT=1 RFA_SLICE=0:30 python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/lift43 ~/src/rvt-extract/out/rfa_chk/lift43_0 > pipeline/logs/rfacheck_lift43_0.log 2>&1
