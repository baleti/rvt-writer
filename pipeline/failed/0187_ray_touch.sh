# timeout=3000
# vm
cd ~/rvt-research/write-lab
TOUCH=1 SAVE='C:\\wl\\out\\tower_touched.rte' SAVELOCAL=generated/tower20_touched_2024.rte python3 tools/ray2.py 2024 scenes/2024_writer_tower20.rte /home/user1/rvt-research/gt_views/2024_writer_tower20.raytouch.tsv '-50,20,6,1,0;-50,20,30,1,0;-50,20,66,1,0;-50,20,126,1,0;-50,20,234,1,0;80,-50,6,0,1;80,-50,126,0,1;80,-50,234,0,1'
