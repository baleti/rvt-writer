#!/bin/bash
# wait for host2, start my overlay VM (CID 30) if it is not running; safe to rerun
until ssh -o ConnectTimeout=8 -o BatchMode=yes host2 true 2>/dev/null; do sleep 120; done
ssh host2 'pgrep -f "guest-cid=30" >/dev/null || { [ $(awk "/MemAvailable/{print int(\$2/1024)}" /proc/meminfo) -gt 6000 ] && cd /srv/vm/win/runs/20261011-194452 && VM_DIR=/srv/vm/win NAME=ci-20261011-194452 CID=30 GPU=0 BALLOON=1 MEM=6G SMP=4 IMG=runs/20261011-194452/disk.qcow2 bash start-vm.sh; }'
sleep 240
for i in 1 2 3 4 5 6 7 8; do python3 -c "
import sys; sys.path.insert(0,'$HOME/rvt-research/write-lab/campaign')
import guest; r=guest.gssh('hostname',30); sys.exit(0 if r.returncode==0 else 1)" && break; sleep 60; done
cd ~/rvt-research/write-lab; mv pipeline/hold/131*_scene_roofs*.sh pipeline/queue/ 2>/dev/null
