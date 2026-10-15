"""recdiff.py SEED FILE_A FILE_B CLASS : first new element of CLASS in A and in B; align decoded fields (name sequence); print differing values and inserted/removed fields"""
import sys,os,difflib; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,wledit
seed,fa,fb,cls=sys.argv[1:5]
a=wledit.Editor(seed); base=set(a.m.ids); del a
def first(f):
    g=rvtgen.Gen(f)
    for tid in sorted(set(g.e.m.ids)-base):
        pn,i,r,log,q=g.e.trace(tid)
        if r['class']==cls: t=g.template(tid); return tid,t
A=first(fa); B=first(fb); print('A',A[0],len(A[1]['rec']),'B',B[0],len(B[1]['rec']))
def seq(t): return [(n,v) for n,s,e,v in t['log'] if n not in('Identifier.m_id64','ElementId.m_id')]
sa,sb=seq(A[1]),seq(B[1]); m=difflib.SequenceMatcher(None,[x[0] for x in sa],[x[0] for x in sb],autojunk=False)
for tag,i1,i2,j1,j2 in m.get_opcodes():
    if tag=='equal':
        for x,y in zip(sa[i1:i2],sb[j1:j2]):
            if x[1]!=y[1] and not (x[0].endswith('m_id') or x[0].startswith('Element.m_id')): print('CHG',x[0],str(x[1])[:90],'->',str(y[1])[:90])
    elif tag=='insert': print('INS',[(n,str(v)[:70]) for n,v in sb[j1:j2]][:40])
    elif tag=='delete': print('DEL',[(n,str(v)[:70]) for n,v in sa[i1:i2]][:40])
    else: print('REPL',[(n,str(v)[:50]) for n,v in sa[i1:i2]][:10],'=>',[(n,str(v)[:50]) for n,v in sb[j1:j2]][:20])
