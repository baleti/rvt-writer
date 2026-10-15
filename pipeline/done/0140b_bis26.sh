# timeout=3000
# vm
cd ~/rvt-research/write-lab
for f in a_walls b_walls_level c_level d_grid_level e_level_walls f_text; do echo CASE $f; python3 tools/open_test.py 2026 generated/bis26/$f.rte bis$f; done; echo CASE roomx; python3 tools/open_test.py 2026 generated/roomx/w_2026.rte bisroomx
