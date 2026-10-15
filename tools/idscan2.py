import sys,os,struct,zlib; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import adiff
R=os.path.expanduser('~/rvt-research/rosetta/')
ids=[int(x) for x in sys.argv[2:]]
for fn in [sys.argv[1]]:
    f=R+fn
    import cfb
    c=cfb.CFB(open(f,'rb').read())
    for n in c.streams():
        try: raw=adiff.graw(f,n)
        except Exception: continue
        for i in ids:
            b=struct.pack('<Q',i); k=-1; h=[]
            while True:
                k=raw.find(b,k+1)
                if k<0: break
                h.append(k)
            if h: print(fn,n,i,len(h),h[:20],flush=True)
        print(fn,n,len(raw),flush=True)
