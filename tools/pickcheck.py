#!/usr/bin/env python3
"""tools/pickcheck.py PICK.tsv : PASS when every Wall and Structural Column of the pickwalls output was hit by a 3D pick ray (doors/windows buried in walls are not required)"""
import sys
bad=0
for l in open(sys.argv[1]):
    if l.startswith('CLS\t'):
        _,k,n,m=l.rstrip('\n').split('\t')
        if k in('Wall:Walls','FamilyInstance:Structural Columns','Floor:Floors') and int(m)>0: bad+=int(m)
    if l.startswith('PICK'): print(l.strip())
    if l.startswith('PHASEFUT_TOTAL') and int(l.split()[1])>0: bad+=int(l.split()[1]); print('PHASE: elements in a LATER phase than the 3D view (invisible in the default GUI 3D view):',l.strip())
print('PICKCHECK','FAIL' if bad else 'PASS','misses',bad); sys.exit(1 if bad else 0)
