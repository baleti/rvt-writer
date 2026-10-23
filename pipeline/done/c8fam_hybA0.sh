# timeout=900
# vm
cd ~/rvt-research/write-lab
for v in P0 P1 P2 P3; do RFA_FLAT=1 python3 /home/user1/src/rvt-extract/oracle/rfacheck.py 2024 /home/user1/src/rvt-extract/out/hybA0/$v /home/user1/src/rvt-extract/out/rfa_chk/hybA0_$v; done
