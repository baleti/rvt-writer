#!/usr/bin/env python3
"""tools/wallcmp.py A.rte B.rte ID... : byte/double level diff of the rec/item/hdr of the same element id in two files"""
import sys,os,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen
A=rvtgen.Gen(sys.argv[1]); B=rvtgen.Gen(sys.argv[2])
for i in map(int,sys.argv[3:]):
    ta,tb=A.template(i),B.template(i)
    for k in ('hdr','rec','item'):
        a,b=ta[k],tb[k]
        if len(a)!=len(b): print(i,k,'LEN',len(a),len(b)); continue
        d=[x for x in range(len(a)) if a[x]!=b[x]]
        out=[]; seen=set()
        for x in d:
            s=x-(x%8)
            if s in seen: continue
            seen.add(s); out.append((s,struct.unpack_from('<d',a,s)[0],struct.unpack_from('<d',b,s)[0]) if s+8<=len(a) else (s,))
        print(i,k,'len',len(a),'bytes differ',len(d),'8-blocks',len(out)); 
        for o in out[:14]: print('    ',o[0],['%.6g'%v for v in o[1:]], a[o[0]:o[0]+8].hex(),b[o[0]:o[0]+8].hex())
