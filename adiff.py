import sys,zlib,struct,difflib; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtw,cfb
def graw(f,n):
    c=cfb.CFB(open(f,'rb').read()); e=c.streams()[n]
    if n in rvtw.PLAIN: return e.data
    P=rvtw.Stream(e.data).payload; i=P.find(rvtw.GZ); return zlib.decompressobj(-15).decompress(P[i+10:])
def ops(a,b,win=48,maxda=600,maxdb=3000):
    i=j=0; out=[]
    while i<len(a) and j<len(b):
        # skip equal run quickly
        k=0
        while i+k<len(a) and j+k<len(b) and a[i+k]==b[j+k]: k+=1
        i+=k; j+=k
        if i>=len(a) or j>=len(b): break
        found=None
        for da in range(0,maxda):
            w=a[i+da:i+da+win]
            if len(w)<win: break
            kk=b.find(w,j,j+maxdb)
            if kk>=0: found=(da,kk-j); break
        if not found: out.append((i,None,j,None)); break
        da,db=found; out.append((i,i+da,j,j+db)); i+=da; j+=db
    return out
if __name__=='__main__':
    f1,f2,n=sys.argv[1:4]; a=graw(f1,n); b=graw(f2,n)
    print(n,len(a),len(b))
    for i0,i1,j0,j1 in ops(a,b):
        print((i0,i1,j0,j1), (a[i0:i1] if i1 else a[i0:i0+30]).hex()[:120],'=>',(b[j0:j1] if j1 else b[j0:j0+30]).hex()[:200])
