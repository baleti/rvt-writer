# timeout=3000
# vm
cd ~/rvt-research/write-lab
for f in a_walls f_text c_level l_plan n_text_floor; do echo CASE $f; python3 tools/open_test.py 2026 generated/bis26p/$f.rte bp$f; done
