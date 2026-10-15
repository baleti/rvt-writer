# timeout=3000
# vm
cd ~/rvt-research/write-lab
for a in '2024 scenes/2024_writer_house_lv.rte 2024_writer_house_lv' '2024 scenes/2024_writer_tower20.rte 2024_writer_tower20' '2024 /home/user1/rvt-research/rosetta/2024_house_base.rte 2024_house_base'; do set -- $a; python3 tools/vis3d.py $1 $2 /home/user1/rvt-research/gt_views/$3.vis.tsv; done
