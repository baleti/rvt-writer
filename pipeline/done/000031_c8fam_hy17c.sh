# timeout=2400
# vm
cd ~/rvt-research/write-lab
 RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/hy17c/ourDITreal ~/src/rvt-extract/out/rfa_chk/hy17c_ourDITreal; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/hy17c/ourALLsmall ~/src/rvt-extract/out/rfa_chk/hy17c_ourALLsmall; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/hy17c/ours ~/src/rvt-extract/out/rfa_chk/hy17c_ours;
