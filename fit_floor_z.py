import sys,os,struct,json,numpy as np; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,genlib2
Y=int(os.environ.get('YEAR',2024)); SUF='' if Y==2024 else '_%d'%Y
f=os.path.expanduser('~/rvt-research/rosetta/%d_floors_lv_base.rte'%Y); g=rvtgen.Gen(f)
ZL=[0.0,10.0,22.0,37.0]; LV=[355,301553,301554,301555]
roles=genlib2.FLOOR_ROLES; ff=json.load(open('files/floorfit%s.json'%SUF))
import wledit
SEEDF={2024:'files/ds0.rte',2026:'files/o26_line.rte'}[Y]
base=set(wledit.Editor(SEEDF).m.ids); new=sorted(set(g.e.m.ids)-base)
lvls=[i for i in new if g.template(i)['cls']=='Level']; rest=[i for i in new if i not in lvls]
ZL=[0.0,10.0,22.0,37.0]
T={}
for k in range(4):
    grp=rest[7*k:7*k+7]+[rest[28+k]]
    for r,i in zip(roles,grp): T[(k,r)]=g.template(i)
out={}
for r in roles:
    for key in ('rec','hdr','item'):
        blobs=[T[(k,r)][key] for k in range(4)]
        if len({len(b) for b in blobs})>1: print('LEN',r,key,[len(b) for b in blobs]); continue
        fd=ff.get(r+'.'+key,{}).get('found',{}); found={}; un=[]
        for o in range(len(blobs[0])-7):
            v=np.array([struct.unpack_from('<d',b,o)[0] for b in blobs])
            if not np.all(np.isfinite(v)) or np.max(np.abs(v))>1e6 or np.any((np.abs(v)<1e-9)&(v!=0)): continue
            pred=np.zeros(4)
            if str(o) in fd:
                fn,co=fd[str(o)]
                for k in range(4):
                    W,D=30+5*k,20+3*k; ft=genlib2._ffeats(0,0,W,D); pred[k]=sum(c*ft[f] for f,c in zip(fn,co))
            res=v-pred
            if np.ptp(res)<1e-9 and np.max(np.abs(res))<1e-9: continue
            A=np.array([[1,z] for z in ZL]); sol=np.linalg.lstsq(A,res,rcond=None)[0]
            if np.max(np.abs(A@sol-res))<1e-7: found[o]=[float(sol[0]),float(sol[1])]
            else: un.append(o)
        out[r+'.'+key]=found; print(r,key,'z-dependent offsets',{k:v for k,v in found.items()},'unexpl',un)
json.dump(out,open('files/floorz%s.json'%SUF,'w'))

sl={}
for k,d in out.items():
    sl[k]={o:(1.0 if v[1]>0 else -1.0) for o,v in d.items() if abs(abs(v[1])-1)<1e-6}
json.dump(sl,open('files/floorslope%s.json'%SUF,'w'))
