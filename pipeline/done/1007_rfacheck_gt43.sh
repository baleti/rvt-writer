# timeout=3300
# vm
cd ~/rvt-research/write-lab
RFA_FLAT=1 python3 -u ~/src/rvt-extract/oracle/rfacheck.py 2024 ~/rvt-research/write-lab/gt_fam/2024_43 ~/src/rvt-extract/out/rfa_chk/gt43 > pipeline/logs/rfacheck_gt43.log 2>&1
