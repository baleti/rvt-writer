#!/usr/bin/env python3
"""tools/classdiff.py SEED FILE CLASS,CLASS,... : decoded field diffs for existing elements of the given classes (small, local-friendly)"""
import sys,os,difflib; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen
a=rvtgen.Gen(sys.argv[1]); b=rvtgen.Gen(sys.argv[2]); cl=set(sys.argv[3].split(','))
for i in sorted(set(a.e.m.ids)&set(b.e.m.ids)):
    c=a.e.trace(i)[2]['class']
    if c not in cl: continue
    x=a.template(i); y=b.template(i)
    if x['rec']==y['rec'] and x['hdr']==y['hdr'] and x['item']==y['item']: continue
    print('==',i,c,len(x['rec']),len(y['rec']),len(x['hdr']),len(y['hdr']))
    for l in difflib.unified_diff([f'{n}={str(v)[:90]}' for n,o,e,v in x['hlog']+x['log']],[f'{n}={str(v)[:90]}' for n,o,e,v in y['hlog']+y['log']],lineterm='',n=0):
        if not l.startswith(('---','+++','@@')) and 'Identifier' not in l and 'ElementId.m_id=' not in l: print(' ',l[:200])
