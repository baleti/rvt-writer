"""idscan.py FILE ID... : find every occurrence of LE64 element ids in all (decompressed) streams; report stream, offset, and the enclosing record's class/id if inside a partition record."""
import sys,os,struct,zlib; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtw,cfb,adiff
f=sys.argv[1]; ids=[int(x) for x in sys.argv[2:]]
c=cfb.CFB(open(f,'rb').read())
for n in c.streams():
    try: raw=adiff.graw(f,n)
    except Exception as e: continue
    for i in ids:
        b=struct.pack('<Q',i); k=-1; hits=[]
        while True:
            k=raw.find(b,k+1)
            if k<0: break
            hits.append(k)
        if hits: print(n,i,len(hits),hits[:12])
