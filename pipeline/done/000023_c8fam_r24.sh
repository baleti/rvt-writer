# timeout=1200
# vm
cd ~/rvt-research/write-lab
RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/r24 ~/src/rvt-extract/out/rfa_chk/r24; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2024 ~/src/rvt-extract/out/r24b ~/src/rvt-extract/out/rfa_chk/r24b; RFA_FLAT=1 python3 ~/bm3-tests/fam/rfacheck_j.py 2026 ~/src/rvt-extract/out/r26 ~/src/rvt-extract/out/rfa_chk/r26
