#!/usr/bin/env python3
"""tools/latest_diff.py ROSETTA_BASE ROSETTA_VAR : differences of Global/Latest between two rosettas. Resyncs on 16-byte anchors (insertions/deletions/replacements), prints each span."""
import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen
def latest(path):
    g=rvtgen.Gen(os.path.expanduser(path)); cap={}
    def f(raw): cap['r']=bytes(raw); return raw
    g.e.global_edit('Global/Latest',f); return cap['r']
def diff(b,v,K=16,W=3000):
    i=j=0; out=[]
    n=len(b); m=len(v)
    while i<n and j<m:
        if b[i]==v[j]: i+=1; j+=1; continue
        si,sj=i,j; best=None
        for d in range(1,W):                          # smallest resync: b[i+di:..]==v[j+dj:..] with di+dj=d
            for di in range(0,d+1):
                dj=d-di; a=b[i+di:i+di+K]
                if len(a)==K and a==v[j+dj:j+dj+K]: best=(di,dj); break
            if best: break
        if not best: out.append((si,n-si,sj,m-sj)); return out
        di,dj=best; out.append((si,di,sj,dj)); i+=di; j+=dj
    if i<n or j<m: out.append((i,n-i,j,m-j))
    return out
if __name__=='__main__':
    b=latest(sys.argv[1]); v=latest(sys.argv[2]); print(len(b),len(v),flush=True)
    for si,di,sj,dj in diff(b,v): print('b@%d del %d  v@%d ins %d'%(si,di,sj,dj),b[si:si+di][:40].hex(),'->',v[sj:sj+dj][:80].hex(),flush=True)
