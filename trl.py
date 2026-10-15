import sys, olefile
sys.path.insert(0,'/home/user1/rvt-research')
from rvtfmt import *
f=sys.argv[1]
o=olefile.OleFileIO(f)
for p in o.listdir(streams=True):
    n='/'.join(p); d=o.openstream(p).read()
    if len(d)>=PAGE_STORED:
        print(n,len(d),len(d)//PAGE_STORED, len(d)%PAGE_STORED)
        for k in range(min(3,len(d)//PAGE_STORED)):
            t=d[k*PAGE_STORED+PAGE_PAYLOAD:(k+1)*PAGE_STORED]
            print(' trailer',k,t[:48].hex(), len(set(t)))
        break
