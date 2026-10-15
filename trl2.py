import sys, olefile, glob, hashlib
sys.path.insert(0,'/home/user1/rvt-research')
from rvtfmt import *
seen={}
for f in sorted(glob.glob('../corpus/2020/*.rvt')+glob.glob('../corpus/2021/*.rvt')):
    o=olefile.OleFileIO(f)
    for p in o.listdir(streams=True):
        n='/'.join(p)
        if not n.startswith('Formats'): continue
        d=o.openstream(p).read()
        for k in range(len(d)//PAGE_STORED):
            pl=d[k*PAGE_STORED:k*PAGE_STORED+PAGE_PAYLOAD]; t=d[k*PAGE_STORED+PAGE_PAYLOAD:(k+1)*PAGE_STORED]
            h=hashlib.md5(pl).hexdigest()
            print(f.split('/')[-1][:20],n,k,h[:8],t[:6].hex())
