# timeout=3600
# vm
cd ~/rvt-research/write-lab
python3 -u tools/smalldump.py 2024 ~/rvt-research/corpus/2024/46_Snowdon_Towers_Sample_Facades.rvt ~/rvt-research/gt_views/2024_46_Snowdon_Towers_Sample_Facades.small.tsv | tail -3
