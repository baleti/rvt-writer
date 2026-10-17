# timeout=2400
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/famsave.py 2024 ~/rvt-research/corpus/2024/43_Snowdon_Towers_Sample_Structural.rvt ~/rvt-research/write-lab/gt_fam/2024_test 'SFD_Rectangle,Callout Head' > pipeline/logs/famsave_test24.log 2>&1
