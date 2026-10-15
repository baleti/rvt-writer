#!/usr/bin/env python3
"""tools/newids.py A B : element ids only in A / only in B, with class"""
import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import wlrec
a=wlrec.Model(sys.argv[1]); b=wlrec.Model(sys.argv[2])
for tag,m,o in (('ONLY_A',a,b),('ONLY_B',b,a)):
    for i in sorted(set(m.ids)-set(o.ids)):
        try: c=m.find(i)
        except Exception as e: c=repr(e)[:60]
        print(tag,i,str(c)[:120])
