# timeout=1200
# vm
cd ~/rvt-research/write-lab
for v in Lat ET CD Fmt Part Ctn; do RFA_FLAT=1 python3 /home/user1/src/rvt-extract/oracle/rfacheck.py 2024 /home/user1/src/rvt-extract/out/hybA0s/$v /home/user1/src/rvt-extract/out/rfa_chk/hybA0s_$v; done
