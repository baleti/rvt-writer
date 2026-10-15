"""fitgen.py : generic differential fitter. For a set of samples (same class/role, known numeric features) find, for every 8-byte double offset in
rec/hdr/item that varies across samples, the sparse linear combination of features reproducing it (<=3 terms, tol 1e-7); offsets that vary but can't be explained are reported.
API: fit_samples(blobs, feats, names, maxterms=3) -> {'found':{off:(terms,coefs)},'unexpl':[off..]}  where blobs=[bytes per sample]
CLI example in fit_columns.py / fit_hosted.py"""
import struct,itertools,json,numpy as np
def fit_samples(blobs,featlist,maxterms=3,tol=1e-7,skip_const=True,offsets=None):
    names=list(featlist[0].keys()); F=np.array([[f[n] for n in names] for f in featlist]); N=min(len(b) for b in blobs)
    if any(len(b)!=N for b in blobs): return None
    found={}; un=[]
    for o in (offsets if offsets is not None else range(N-7)):
        v=np.array([struct.unpack_from('<d',b,o)[0] for b in blobs])
        if not np.all(np.isfinite(v)) or np.max(np.abs(v))>1e6 or np.ptp(v)<1e-12 or np.any((np.abs(v)<1e-9)&(v!=0)): continue
        ok=None
        for r in range(1,maxterms+1):
            for comb in itertools.combinations(range(len(names)),r):
                A=F[:,comb]; sol=np.linalg.lstsq(A,v,rcond=None)[0]
                if np.max(np.abs(A@sol-v))<tol: ok=(comb,sol); break
            if ok: break
        if ok: found[o]=([names[i] for i in ok[0]],[round(float(s),10) for s in ok[1]])
        else: un.append(o)
    return dict(found={str(k):v for k,v in found.items()},unexpl=un)
def apply_fit(buf,fit,feat):
    b=bytearray(buf)
    for off,(fn,co) in fit['found'].items(): struct.pack_into('<d',b,int(off),sum(c*feat[f] for f,c in zip(fn,co)))
    return b
