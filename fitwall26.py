import sys,os,struct,math,json; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import numpy as np, rvtgen
rows=[l.split() for l in open('files/kwalls60_26.txt') if l.strip()]
ws=[(int(r[1]),int(r[2]),float(r[3]),float(r[4]),float(r[5]),float(r[6]),float(r[7]),float(r[8])) for r in rows]   # id,level,x0,y0,x1,y1,h,z0
g=rvtgen.Gen('files/kwalls60_26.rte')
T={w[0]:g.template(w[0]) for w in ws}
def feats(w):
    _,lv,x0,y0,x1,y1,h,z0=w; L=math.hypot(x1-x0,y1-y0); dx=(x1-x0)/L; dy=(y1-y0)/L
    return {'1':1.0,'x0':x0,'y0':y0,'x1':x1,'y1':y1,'dx':dx,'dy':dy,'L':L,'h':h,'z0':z0,'dxx0':dx*x0,'dxy0':dx*y0,'dyx0':dy*x0,'dyy0':dy*y0,'ang':math.atan2(dy,dx),'z1':z0+h,'xm':(x0+x1)/2,'ym':(y0+y1)/2,'dxxm':dx*(x0+x1)/2,'dxym':dx*(y0+y1)/2,'dyxm':dy*(x0+x1)/2,'dyym':dy*(y0+y1)/2,'L2':L/2,'h2':h/2}
names=list(feats(ws[0]).keys()); F=np.array([[feats(w)[k] for k in names] for w in ws])
def fit(vals):
    # sparse fit: try single, pair, triple term combos greedily via lstsq on subsets of increasing size
    import itertools
    best=None
    for r in (1,2,3,4):
        for comb in itertools.combinations(range(len(names)),r):
            A=F[:,comb]; sol,res,rk,sv=np.linalg.lstsq(A,vals,rcond=None)
            err=np.max(np.abs(A@sol-vals))
            if err<1e-7: return comb,sol,err
    return None
out={}
for key in ('rec','hdr','item'):
    N=len(T[ws[0][0]][key]); data=[T[w[0]][key] for w in ws]
    found={}; unexplained=[]
    for o in range(0,N-7):
        vals=np.array([struct.unpack_from('<d',d,o)[0] for d in data])
        if not np.all(np.isfinite(vals)) or np.max(np.abs(vals))>1e5 or np.ptp(vals)<1e-12: continue
        # skip denormals/garbage: require values 'reasonable'
        if np.any((np.abs(vals)<1e-9)&(vals!=0)): continue
        f=fit(vals)
        if f: found[o]=([names[i] for i in f[0]],[round(float(s),9) for s in f[1]])
        else: unexplained.append(o)
    out[key]=dict(found={str(k):v for k,v in found.items()},unexpl=unexplained)
    print(key,'fitted offsets',len(found),'unexplained candidate offsets',len(unexplained))
json.dump(out,open('files/wallfit_26.json','w'))
