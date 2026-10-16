# timeout=3600
# vm
cd ~/rvt-research/write-lab
python3 -u tools/smalldump.py 2026 ~/rvt-research/corpus/2026/58_Snowdon_Towers_Sample_Facades.rvt ~/rvt-research/gt_views/2026_58_Snowdon_Towers_Sample_Facades.small.tsv | tail -3
