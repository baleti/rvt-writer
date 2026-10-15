#!/usr/bin/env python3
"""tools/keycheck.py FILE.rte LOG [ids...] : compare genlib.spatial_key(hdr outline) with the key stored in every Revit wall of FILE listed in LOG (W lines)"""
import sys,os,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,genlib
G=rvtgen.Gen(sys.argv[1]); bad=0; n=0
for l in open(sys.argv[2]):
    if not l.startswith('W '): continue
    p=l.split(); wid=int(p[1]); t=G.template(wid); hl={x[0]:x for x in t['hlog']}; bb=struct.unpack_from('<6d',t['hdr'],hl['Outline.m_minmax'][1]); tok=t['item'][316:320]
    try: k=genlib.spatial_key(bb)
    except Exception as e: k=b'ERR'
    n+=1
    if k!=tok: bad+=1; print(p[2:],['%.2f'%v for v in bb],'rev',tok.hex(),'mine',k.hex())
print('walls',n,'mismatch',bad)
