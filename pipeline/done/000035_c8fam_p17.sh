# timeout=3600
# vm
cd ~/rvt-research/write-lab
 RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/p2017 ~/src/rvt-extract/out/rfa_chk/r_p2017; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/p2018 ~/src/rvt-extract/out/rfa_chk/r_p2018;
