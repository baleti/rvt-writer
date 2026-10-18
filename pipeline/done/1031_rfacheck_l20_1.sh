# timeout=900
# vm
cd ~/rvt-research/write-lab
RFA_FLAT=1 RFA_SLICE=10:20 python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/src/rvt-extract/out/lift20 ~/src/rvt-extract/out/rfa_chk/l20_1 > pipeline/logs/rfacheck_l20_1.log 2>&1
