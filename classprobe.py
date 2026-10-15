"""classprobe.py SEED FILE : list elements of FILE that are not in SEED with class, record length, zone record count (offline; no Revit)"""
import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,wledit
seed,f=sys.argv[1:3]
a=wledit.Editor(seed); base=set(a.m.ids); del a
g=rvtgen.Gen(f); out=[]
for tid in sorted(set(g.e.m.ids)-base):
    try:
        L=g.locate(tid); pn,i,r,log,q=g.e.trace(tid)
        out.append((tid,r['class'],L['rec'][1],len(L['zone']),L['hdr'][1]))
    except Exception as ex: out.append((tid,'ERR '+str(ex)[:40],0,0,0))
from collections import Counter
print(Counter(o[1] for o in out))
for o in out: print(*o,sep='\t')
