# timeout=2400
# vm
cd ~/rvt-research/write-lab
RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/q2017 ~/src/rvt-extract/out/rfa_chk/q2017; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/q2018 ~/src/rvt-extract/out/rfa_chk/q2018
