# timeout=3600
# vm
cd ~/rvt-research/write-lab
python3 rvt_write.py finish 2026 scenes/2026_writer_spec_example2.rte generated/fin/spec_fin_2026.rte specs/finish_example.json scenes/2026_writer_spec_example2.rte.json 2>&1 | tail -4
mkdir -p generated/pick
python3 tools/pickwalls.py 2026 generated/fin/spec_fin_2026.rte generated/pick/2026_specfin.tsv | tail -1
python3 tools/pickcheck.py generated/pick/2026_specfin.tsv
