# timeout=3000
# vm
cd ~/rvt-research/write-lab
for f in g_floor h_col i_walls20 j_text20 k_text80 l_plan m_walls_plan; do echo CASE $f; python3 tools/open_test.py 2026 generated/bis26/$f.rte bis$f; done
