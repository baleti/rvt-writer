#!/bin/bash
# vmw.sh put LOCAL GUESTPATH | get GUESTPATH LOCAL | ps 'cmd' | up YEAR | down YEAR | job YEAR TAG FILE_GUEST [audit] [saveas]
RD=${RVT_RD:-/srv/vm/win/runs/20261011-194452}
h2(){ ssh -i $K -o BatchMode=yes $H "$@"; }
case $1 in
 put) scp -q -i $K "$2" $H:/tmp/wl_put.tmp && h2 "$RD/gcp /tmp/wl_put.tmp 'GUEST:$3'; rm -f /tmp/wl_put.tmp";;
 get) h2 "rm -rf /tmp/wl_get.tmp; $RD/gcp -r 'GUEST:$2' /tmp/wl_get.tmp" && scp -q -r -i $K $H:/tmp/wl_get.tmp "$3";;
 ps) h2 "$RD/gssh powershell -NoProfile -Command \"$2\"";;
 psf) $0 put "$2" C:/wl/_psf.ps1 >/dev/null; h2 "$RD/gssh powershell -NoProfile -ExecutionPolicy Bypass -File C:/wl/_psf.ps1";;
 up) h2 "$RD/gssh powershell -NoProfile -ExecutionPolicy Bypass -File C:/ci/revit-up.ps1 -Year $2";;
 down) h2 "$RD/gssh powershell -NoProfile -ExecutionPolicy Bypass -File C:/ci/revit-down.ps1 -Year $2";;
 job) # YEAR TAG FILE [audit] [saveas]
  Y=$2; T=$3; F=$4; A=${5:-false}; S=${6:-false}
  sed "s#__FILE__#$F#;s#__TAG__#$T#;s#__AUDIT__#$A#;s#__SAVEAS__#$S#" ~/rvt-research/write-lab/jobs/dump.cs > /tmp/claude-1000/job_$T.cs
  $0 put /tmp/claude-1000/job_$T.cs "C:/wl/job_$T.cs" >/dev/null
  P=$(cat ~/rvt-research/write-lab/ports_$Y 2>/dev/null)
  h2 "$RD/gssh powershell -NoProfile -ExecutionPolicy Bypass -File C:/wl/run.ps1 -Port $P -Job C:/wl/job_$T.cs";;
esac
