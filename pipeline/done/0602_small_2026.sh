# timeout=3600
# vm
cd ~/rvt-research/write-lab
python3 -u tools/smalldump.py 2026 ~/rvt-research/corpus/2026/55_Snowdon_Towers_Sample_Structural.rvt ~/rvt-research/gt_views/2026_55_Snowdon_Towers_Sample_Structural.small.tsv | tail -3
