# timeout=3600
# vm
cd ~/rvt-research/write-lab
python3 -u tools/smalldump.py 2024 ~/rvt-research/corpus/2024/43_Snowdon_Towers_Sample_Structural.rvt ~/rvt-research/gt_views/2024_43_Snowdon_Towers_Sample_Structural.small.tsv; tail -c 400 ~/rvt-research/gt_views/2024_43_Snowdon_Towers_Sample_Structural.small.tsv
