#!/bin/bash
# enqueue.sh NAME TIMEOUT 'command...' : add a job (prefix auto-ordered by time unless NAME starts with digits)
D=$(dirname "$0"); n=$1; [[ $n =~ ^[0-9] ]] || n=$(date +%H%M%S)_$n
printf '# timeout=%s\n# vm\ncd ~/rvt-research/write-lab\n%s\n' "$2" "$3" > $D/queue/$n.sh; echo queued $n
