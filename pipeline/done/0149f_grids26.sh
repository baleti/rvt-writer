# timeout=3600
# vm
cd ~/rvt-research/write-lab
python3 tools/open_test.py 2026 generated/bis26p/d_grid_level.rte bpgrid; pipeline/stageb_job.sh grids1 2026 generated/stageb/grids1_2026.rte /home/user1/rvt-research/rosetta/2026_house_base.rte
