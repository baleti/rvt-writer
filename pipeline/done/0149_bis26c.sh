# timeout=3000
# vm
cd ~/rvt-research/write-lab
for f in n_text_floor o_level_floor p_rect_floor q_text_walls20 r_floor_text; do echo CASE $f; python3 tools/open_test.py 2026 generated/bis26/$f.rte bis$f; done
