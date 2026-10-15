#!/bin/bash
# stageb_geom.sh YEAR FILE MANIFEST : Revit geometry export of a writer-built file + comparison with the manifest
cd ~/rvt-research/write-lab
timeout 2400 python3 -u geomexport.py $1 $2 --chunk 6000 --fam 3 --out generated/stageb/gt | tail -2
python3 stageb_check.py generated/stageb/gt/$1_$(basename $2).tsv $3
