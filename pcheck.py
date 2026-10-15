import sys,struct; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtw,cfb,wlpart
f=sys.argv[1]
c=cfb.CFB(open(f,'rb').read())
for sn,e in c.streams().items():
    if sn.startswith('Partitions/'): p=wlpart.Partition(rvtw.Stream(e.data))
bad=0; n220=0
for k,m in enumerate(p.mem):
    g=p.hdr if k==0 else p.gaps[k-1]
    if k>0 and len(g)!=32: n220+=1; continue
    off=24 if k==0 else 12
    x1=struct.unpack_from('<I',g,off)[0]; x2=struct.unpack_from('<I',g,off+8)[0]; hs=m['hs']
    raw=bytes(m['raw']); pos=[]; q=-4
    while q+hs<=len(raw):
        q+=hs+struct.unpack_from('<I',raw,q+hs-4)[0]
        if q+4>len(raw): break
        pos.append(q)
    cnt=len(pos)
    ok=(x2==len(raw)-hs*x1) and (cnt==x1)
    if not ok:
        bad+=1
        if bad<=8: print('member',k,'len',len(raw),'hs',hs,'x1',x1,'walk',cnt,'x2',x2,'expect',len(raw)-hs*x1, 'endq',q+4-len(raw))
print(f,'members',p.n,'bad',bad)
