# timeout=3000
# vm
cd ~/rvt-research/write-lab
G=generated/roomx; python3 rvt_write.py scene specs/roomx_2024.json $G/w_2024.rte || exit 1; for m in none touch room; do python3 tools/finish_all.py 2024 $G/w_2024.rte $G/w_2024_$m.rte specs/fin_$m.json $G/w_2024.rte.json || exit 1; done; ls -la $G
