import sys,glob,collections
sys.path.insert(0,'/home/user1/rvt-research/write-lab'); sys.path.insert(0,'/home/user1/rvt-research')
import cfb, ecc
from rvtfmt import *
files=sorted(glob.glob('../corpus/20*/*.rv?'))
if len(sys.argv)>1: files=files[:int(sys.argv[1])]
ok=bad=0; badN=collections.Counter(); okN=set()
for f in files:
    c=cfb.CFB(open(f,'rb').read())
    for k,e in c.streams().items():
        d=e.data
        if k in('ProjectInformation','TransmissionData','BasicFileInfo','Contents','RevitPreview4.0'): continue
        full=len(d)//PAGE_STORED
        pages=[d[i*PAGE_STORED:(i+1)*PAGE_STORED] for i in range(full)]
        last=d[full*PAGE_STORED:]
        if len(last)>=90: pages.append(last)
        for p in pages:
            if ecc.params(len(p)) and ecc.check(p): ok+=1; okN.add(len(p))
            else: bad+=1; badN[(len(p),k)]+=1
print('ok',ok,'bad',bad); print(badN.most_common(20))
