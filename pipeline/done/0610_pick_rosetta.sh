# timeout=3000
# vm
cd ~/rvt-research/write-lab
python3 tools/pickwalls.py 2024 ~/rvt-research/rosetta/2024_railing_shift_base.rte generated/pick/2024_railing_base.tsv | tail -1; python3 tools/pickcheck.py generated/pick/2024_railing_base.tsv | tail -3; python3 tools/pickwalls.py 2024 ~/rvt-research/rosetta/2024_curtain_shift_base.rte generated/pick/2024_curtain_base.tsv | tail -1
