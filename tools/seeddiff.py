#!/usr/bin/env python3
"""tools/seeddiff.py SEED FILE [OUT] : which SEED elements does FILE change (rec/hdr/item bytes), with decoded field diffs. CPU minutes: run on host1."""
import sys,os,difflib; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen
a=rvtgen.Gen(sys.argv[1]); b=rvtgen.Gen(sys.argv[2]); out=open(sys.argv[3],'w') if len(sys.argv)>3 else sys.stdout
ra,rb=a.bj,b.bj
for i in sorted(set(a.e.m.ids)&set(b.e.m.ids)):
    try: x=a.template(i); y=b.template(i)
    except Exception as ex: print('ERR',i,ex,file=out); continue
    if x['rec']==y['rec'] and x['hdr']==y['hdr'] and x['item']==y['item']: continue
    print('==',i,x['cls'],len(x['rec']),len(y['rec']),len(x['hdr']),len(y['hdr']),file=out)
    for l in difflib.unified_diff([f'{n}={str(v)[:90]}' for n,o,e,v in x['hlog']+x['log']],[f'{n}={str(v)[:90]}' for n,o,e,v in y['hlog']+y['log']],lineterm='',n=0):
        if not l.startswith(('---','+++','@@')) and 'Identifier' not in l and 'ElementId.m_id=' not in l: print(' ',l[:200],file=out)
    out.flush()
