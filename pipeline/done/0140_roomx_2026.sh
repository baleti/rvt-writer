# timeout=3000
# vm
cd ~/rvt-research/write-lab
G=generated/roomx; python3 rvt_write.py scene specs/roomx_2026.json $G/w_2026.rte || exit 1; for m in none touch room; do python3 tools/finish_all.py 2026 $G/w_2026.rte $G/w_2026_$m.rte specs/fin_$m.json $G/w_2026.rte.json || exit 1; done; ls -la $G
