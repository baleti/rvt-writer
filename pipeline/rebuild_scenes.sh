#!/bin/bash
# rebuild_scenes.sh YEAR scene... : rebuild each scene (current writer), vcheck, enqueue full protocol + 3D pick check (queue number prefix 04NN)
cd ~/rvt-research/write-lab
Y=$1; shift
SEED=~/rvt-research/rosetta/${Y}_house_base.rte
i=${QSTART:-400}
for arg in "$@"; do
  sc=${arg%%:*}; nm=${arg##*:}
  f=generated/stageb/${nm}_${Y}.rte
  systemd-run --user --scope -q -p MemoryMax=3G -p MemorySwapMax=0 nice -n 19 timeout 1200 python3 scenes.py $sc $f $Y > /dev/null 2>&1
  r=$(systemd-run --user --scope -q -p MemoryMax=3G -p MemorySwapMax=0 nice -n 19 timeout 900 python3 vcheck.py $f --seed $SEED --manifest $f.json 2>&1 | tail -1)
  echo "$nm $Y vcheck: $r"
  case "$r" in *"PASS 0 errors"*)
    printf '# timeout=3600\n# vm\ncd ~/rvt-research/write-lab\npipeline/stageb_job.sh %s %s %s %s\nmkdir -p generated/pick\npython3 tools/pickwalls.py %s %s generated/pick/%s_%s.tsv | tail -1\npython3 tools/pickcheck.py generated/pick/%s_%s.tsv\n' $nm $Y $f $SEED $Y $f $Y $nm $Y $nm > pipeline/queue/0${i}_scene_${nm}_$Y.sh;;
  esac
  i=$((i+1))
done
