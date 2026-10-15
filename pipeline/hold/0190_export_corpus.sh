# timeout=14400
# vm
cd ~/rvt-research/write-lab
for a in '2026 2026/55_Snowdon_Towers_Sample_Structural' '2024 2024/43_Snowdon_Towers_Sample_Structural' '2024 2024/46_Snowdon_Towers_Sample_Facades' '2026 2026/58_Snowdon_Towers_Sample_Facades'; do set -- $a; python3 oracle_run.py export $1 /home/user1/rvt-research/corpus/$2.rvt; done
