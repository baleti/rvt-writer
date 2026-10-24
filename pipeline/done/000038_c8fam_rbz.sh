# timeout=3600
# vm
cd ~/rvt-research/write-lab
 RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/rb17z_A_realcuts_ourgz ~/src/rvt-extract/out/rfa_chk/rb17z_A_realcuts_ourgz; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/rb17z_C_realcuts_realgz ~/src/rvt-extract/out/rfa_chk/rb17z_C_realcuts_realgz;
