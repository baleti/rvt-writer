#!/usr/bin/env python3
"""tools/wallvar3.py SPEC.json OUT.rte : ablation of the item geometry token on x-running writer walls (ids 301592+1..). variants hard-coded below"""
import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import json,genlib,rvt_write
spec,out=sys.argv[1:3]
N=bytes.fromhex('d1000001'); N80=bytes.fromhex('d1800001'); orig=genlib.make_wall
V=[{o:bytes.fromhex(h) for o in (316,472,628,706,550)} for h in ('00000000','ffffffff','01000000','00000001','7fffffff','80000000','d1000001','ffffff00')]
cnt=[0]
def mw(g,T,nid,*a,**k):
    hdr,rec,item,row=orig(g,T,nid,*a,**k); it=bytearray(item); v=V[cnt[0]]; cnt[0]+=1
    for o,b in v.items(): it[o:o+4]=b
    return hdr,rec,bytes(it),row
genlib.make_wall=mw
rvt_write.build(json.load(open(spec)),out)
