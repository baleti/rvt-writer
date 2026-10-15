# timeout=3000
# vm
cd ~/rvt-research/write-lab
python3 tools/ray2.py 2024 scenes/2024_writer_tower20.rte /home/user1/rvt-research/gt_views/2024_writer_tower20.ray.tsv '-50,20,6,1,0;-50,20,30,1,0;-50,20,66,1,0;-50,20,126,1,0;-50,20,234,1,0;80,-50,6,0,1;80,-50,126,0,1'; python3 tools/ray2.py 2024 ~/rvt-research/rosetta/2024_house_base.rte /home/user1/rvt-research/gt_views/2024_house_base.ray.tsv '-50,13,5,1,0;-50,5,5,1,0;20,-50,5,0,1'
