import sys,glob,collections
sys.path.insert(0,'/home/user1/rvt-research/write-lab'); sys.path.insert(0,'/home/user1/rvt-research')
import cfb, ecc, numpy as np
from rvtfmt import *
ecc.POLY[8]=0b100011101   # x^8+x^4+x^3+x^2+1 (primitive)
def par_with(page,d,u):
    N=len(page); B=8*N; L=B//u
    cap=(u*(L-d))//8
    bits=np.unpackbits(np.frombuffer(page[:cap],dtype=np.uint8),bitorder='little')
    full=np.zeros(B,dtype=np.uint8); full[:len(bits)]=bits
    grid=full[:u*L].reshape(L,u); mask=(1<<d)-1; taps=ecc.POLY[d]&mask
    st=np.zeros(u,dtype=np.int64)
    for t in range(L-d):
        fb=((st>>(d-1))&1)^grid[t]; st=((st<<1)&mask)^(fb*taps)
    for tp in range(d): grid[L-d+tp]=(st>>(d-1-tp))&1
    full[:u*L]=grid.reshape(-1)
    return np.packbits(full,bitorder='little').tobytes()==page
f=sorted(glob.glob('../corpus/20*/*.rv?'))[0]
c=cfb.CFB(open(f,'rb').read())
for k,e in c.streams().items():
    d=e.data
    if k in('ProjectInformation','TransmissionData','BasicFileInfo','Contents','RevitPreview4.0'): continue
    full=len(d)//PAGE_STORED
    pages=[d[i*PAGE_STORED:(i+1)*PAGE_STORED] for i in range(full)]
    last=d[full*PAGE_STORED:]
    if len(last)>=90: pages.append(last)
    for p in pages:
        if ecc.check(p): continue
        N=len(p); B=8*N; hits=[]
        for dd in (3,4,5,6,7,8,9,10,11):
            for u in range(40,min(B//2,1200)):
                if B%u<=7 and (B//u)-dd>0 and par_with(p,dd,u): hits.append((dd,u))
        print(k,N,'rule',ecc.params(N),'hits',hits,flush=True)
