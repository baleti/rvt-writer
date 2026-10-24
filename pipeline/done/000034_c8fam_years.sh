# timeout=3600
# vm
cd ~/rvt-research/write-lab
 RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/z2021 ~/src/rvt-extract/out/rfa_chk/r_z2021; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/q2018 ~/src/rvt-extract/out/rfa_chk/r_q2018; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/q2017 ~/src/rvt-extract/out/rfa_chk/r_q2017;
