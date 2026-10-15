W=$HOME/rvt-research/write-lab
python3 -u $W/tools/seeddiff.py $W/files/o26_line.rte $HOME/rvt-research/rosetta/2026_grid_level_base.rte $W/generated/seeddiff_grid26.txt
python3 -u $W/fit_roofs.py 2024
python3 -u $W/fit_roofs.py 2026
