#!/usr/bin/env python3
"""tools/wallvar2.py SPEC.json OUT.rte REVIT.rte ID:KIND,... : splice item byte ranges from the same-id Revit wall. KIND: tok (token ranges) | stamp (item 8:12) | nontok (everything else that differs) | all"""
import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import json,genlib,rvtgen,rvt_write
spec,out,rev,vm=sys.argv[1:5]; var={int(k):v for k,v in (x.split(':') for x in vm.split(','))}
B=rvtgen.Gen(rev); orig=genlib.make_wall
TOK=[(316,320),(472,476),(550,554),(628,632),(706,710)]
def mw(g,T,nid,*a,**k):
    hdr,rec,item,row=orig(g,T,nid,*a,**k)
    if nid in var:
        r=B.template(nid)['item']; it=bytearray(item); kd=var[nid]
        tokset=set(i for s,e in TOK for i in range(s,e))
        for i in range(len(it)):
            if it[i]==r[i]: continue
            c='stamp' if 8<=i<12 else 'tok' if i in tokset else 'nontok'
            if kd=='all' or kd==c: it[i]=r[i]
        item=bytes(it)
    return hdr,rec,item,row
genlib.make_wall=mw
rvt_write.build(json.load(open(spec)),out)
