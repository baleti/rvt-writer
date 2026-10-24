# timeout=2400
# vm
cd ~/rvt-research/write-lab
 RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/samp16 ~/src/rvt-extract/out/rfa_chk/samp16; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/samp17 ~/src/rvt-extract/out/rfa_chk/samp17; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/samp18 ~/src/rvt-extract/out/rfa_chk/samp18; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/samp19 ~/src/rvt-extract/out/rfa_chk/samp19;
