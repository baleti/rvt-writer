#!/usr/bin/env python3
"""tools/wallvar.py SPEC.json OUT.rte REVIT.rte VARMAP : build SPEC but splice parts of Revit-made walls (same ids) into writer walls. VARMAP 'id:parts,...' parts subset of hri (hdr rec item)"""
import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import json,genlib,rvtgen,rvt_write
spec,out,rev,vm=sys.argv[1:5]; var={int(k):v for k,v in (x.split(':') for x in vm.split(','))}
B=rvtgen.Gen(rev); orig=genlib.make_wall
def mw(g,T,nid,*a,**k):
    hdr,rec,item,row=orig(g,T,nid,*a,**k)
    if nid in var:
        t=B.template(nid); p=var[nid]
        if 'h' in p: hdr=t['hdr']
        if 'r' in p: rec=t['rec']
        if 'i' in p: item=t['item']
    return hdr,rec,item,row
genlib.make_wall=mw
rvt_write.build(json.load(open(spec)),out)
