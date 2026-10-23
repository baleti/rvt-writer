# timeout=1200
# vm
cd ~/rvt-research/write-lab
for v in none cat win both; do RFA_FLAT=1 python3 /home/user1/src/rvt-extract/oracle/rfacheck.py 2024 /home/user1/src/rvt-extract/out/hybA0u/$v /home/user1/src/rvt-extract/out/rfa_chk/hybA0u_$v; done
