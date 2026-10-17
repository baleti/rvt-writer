# timeout=2400
# vm
cd ~/rvt-research/write-lab
python3 -u ~/src/rvt-extract/oracle/famsave.py 2020 ~/rvt-research/corpus/2020/18_rst_basic_sample_project.rvt ~/rvt-research/write-lab/gt_fam/2020_test 'M_Baluster - Square,Round Bar' > pipeline/logs/famsave_test.log 2>&1
