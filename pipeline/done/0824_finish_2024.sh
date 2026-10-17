# timeout=3600
# vm
cd ~/rvt-research/write-lab
python3 rvt_write.py finish 2024 scenes/2024_writer_spec_example2.rte generated/fin/spec_fin_2024.rte specs/finish_example.json scenes/2024_writer_spec_example2.rte.json 2>&1 | tail -4
mkdir -p generated/pick
python3 tools/pickwalls.py 2024 generated/fin/spec_fin_2024.rte generated/pick/2024_specfin.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2024_specfin.tsv
