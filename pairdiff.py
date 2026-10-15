"""pairdiff.py SEED BASE VAR : for each class, pair the k-th element added in BASE with the k-th same-class element in VAR's translated copy; print differing record offsets with float64 interpretation"""
import sys,os,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,wledit
seed,fb,fv=sys.argv[1:4]
a=wledit.Editor(seed); base=set(a.m.ids); del a
def recs(f,skip):
    g=rvtgen.Gen(f); d={}
    for tid in sorted(set(g.e.m.ids)-skip):
        L=g.locate(tid); pn,i,r,log,q=g.e.trace(tid); d.setdefault(r['class'],[]).append((tid,bytes(g.bj[L['rec'][0]:L['rec'][0]+L['rec'][1]]),g))
    return d
B=recs(fb,base); allb=set()
for v in B.values(): allb|={t for t,_,_ in v}
V=recs(fv,base|allb)
for cls,lst in B.items():
    vl=V.get(cls,[])
    print('==',cls,len(lst),'base;',len(vl),'copies')
    for (t,rb,_),(t2,rv,_) in list(zip(lst,vl))[:2]:
        if len(rb)!=len(rv): print('  len differ',t,len(rb),t2,len(rv)); continue
        diffs=[k for k in range(len(rb)) if rb[k]!=rv[k]]
        # collapse to 8-byte windows
        seen=set(); outl=[]
        for k in diffs:
            o=k&~7
            if o in seen or o+8>len(rb): continue
            seen.add(o); x=struct.unpack_from('<d',rb,o)[0]; y=struct.unpack_from('<d',rv,o)[0]
            outl.append('%d:%.4g->%.4g'%(o,x,y) if abs(x)<1e9 and abs(y)<1e9 else '%d:raw'%o)
        print('  ',t,t2,len(diffs),'bytes differ:',' '.join(outl[:40]))
