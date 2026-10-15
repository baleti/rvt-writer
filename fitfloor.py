import sys,os,struct,math,json,itertools; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import numpy as np, rvtgen, wledit
Y=int(os.environ.get('YEAR',2024)); SUF='' if Y==2024 else '_%d'%Y; SEEDF={2024:'files/ds0.rte',2026:'files/o26_line.rte'}[Y]
seed,f=os.path.expanduser('~/rvt-research/write-lab/'+SEEDF),os.path.expanduser('~/rvt-research/rosetta/%d_floors12_base.rte'%Y)
R=[(0,0,40,26),(50,0,30,20),(100,5,12,12),(0,50,25,8),(40,50,10,30),(70,50,33,17),(110,50,20,40),(0,100,15,15),(30,100,60,10),(100,100,8,22),(120,100,45,45),(0,130,18,9)]
a=wledit.Editor(seed); base=set(a.m.ids); del a
g=rvtgen.Gen(f); new=sorted(set(g.e.m.ids)-base); assert len(new)==96,len(new)
roles=['sp','vs','fl','c0','c1','c2','c3','c4']
T={}
for k in range(12):
    for j,tid in enumerate(new[7*k:7*k+7]+[new[84+k]]): T[(k,roles[j])]=g.template(tid)
def feats(r):
    x0,y0,W,D=r; return {'1':1.0,'x0':x0,'y0':y0,'W':W,'D':D,'x1':x0+W,'y1':y0+D,'xm':x0+W/2,'ym':y0+D/2,'WD':W*D,'W2D2':2*(W+D),'hW':W/2,'hD':D/2,'D13':D/3,'D23':2*D/3,'xsd':x0+W/2-D/3,'nD13':-D/3}
KS=[k for k in range(12) if R[k][2]>=R[k][3]]
names=list(feats(R[0]).keys()); F=np.array([[feats(R[k])[n] for n in names] for k in KS])
def fit(vals):
    for r in (1,2,3):
        for comb in itertools.combinations(range(len(names)),r):
            A=F[:,comb]; sol=np.linalg.lstsq(A,vals,rcond=None)[0]
            if np.max(np.abs(A@sol-vals))<1e-7: return comb,sol
    return None
out={}
for role in roles:
    for key in ('rec','hdr','item'):
        N=len(T[(0,role)][key]); data=[T[(k,role)][key] for k in KS]
        if any(len(d)!=N for d in data): print('LEN VARIES',role,key); continue
        found={}; un=[]
        for o in range(N-7):
            vals=np.array([struct.unpack_from('<d',d,o)[0] for d in data])
            if not np.all(np.isfinite(vals)) or np.max(np.abs(vals))>1e5 or np.ptp(vals)<1e-12 or np.any((np.abs(vals)<1e-9)&(vals!=0)): continue
            r=fit(vals)
            if r: found[o]=([names[i] for i in r[0]],[round(float(s),10) for s in r[1]])
            else: un.append(o)
        out[role+'.'+key]=dict(found={str(k):v for k,v in found.items()},unexpl=un)
        print(role,key,'fitted',len(found),'unexplained',un[:10])
json.dump(out,open(os.path.expanduser('~/rvt-research/write-lab/files/floorfit%s.json'%SUF),'w'))
