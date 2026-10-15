import sys,zlib,struct; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtw,cfb
def raws(f):
    c=cfb.CFB(open(f,'rb').read()); out={}
    for sn,e in c.streams().items():
        if sn in rvtw.PLAIN or sn.startswith('Partitions/'): 
            out[sn]=e.data if sn in rvtw.PLAIN else None; continue
        P=rvtw.Stream(e.data).payload; i=P.find(rvtw.GZ)
        do=zlib.decompressobj(-15); raw=do.decompress(P[i+10:]); out[sn]=(P[:i],raw)
    return out
a=raws(sys.argv[1]); b=raws(sys.argv[2])
for sn in a:
    x,y=a[sn],b.get(sn)
    if x is None or sn.startswith('Partitions'): continue
    if isinstance(x,bytes): print(sn,'plain', x==y, len(x),len(y) if y else None); continue
    pa,ra=x; pb,rb=y
    if ra==rb and pa==pb: print(sn,'same'); continue
    d=[k for k in range(min(len(ra),len(rb))) if ra[k]!=rb[k]]
    print(sn,'prefix',pa.hex(),pb.hex(),'len',len(ra),len(rb),'first diffs',d[:12],'ndiff',len(d))
