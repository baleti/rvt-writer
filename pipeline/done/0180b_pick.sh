# timeout=3000
# vm
cd ~/rvt-research/write-lab
for a in '2024 2024_writer_tower20' '2024 2024_writer_office7' '2024 2024_writer_house1' '2024 2024_writer_campus4' '2026 2026_writer_tower20' '2026 2026_writer_office7'; do set -- $a; python3 tools/pickprobe.py $1 scenes/$2.rte /home/user1/rvt-research/gt_views/$2.pick.tsv; done; python3 tools/pickprobe.py 2024 ~/rvt-research/rosetta/2024_house_base.rte /home/user1/rvt-research/gt_views/2024_house_base.pick.tsv
