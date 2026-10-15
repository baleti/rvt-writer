import sys,struct,zlib; sys.path.insert(0,'/home/user1/rvt-research/write-lab'); sys.path.insert(0,'/home/user1/rvt-research')
import adiff,rvtw,cfb,wlpart
a,b=sys.argv[1:3]
for n in ('Global/ElemTable','Global/History','Global/DocumentIncrementTable'):
    x=adiff.graw(a,n); y=adiff.graw(b,n); print(n,len(x),len(y),'newrows' if 'Elem' in n else '')
    if 'Elem' in n:
        na=struct.unpack_from('<I',x,2)[0]; nb=struct.unpack_from('<I',y,2)[0]
        ra={x[6+40*k:6+40*k+40] for k in range(na)}; 
        for k in range(nb):
            r=y[6+40*k:6+40*k+40]
            if r not in ra: print('  row',struct.unpack('<Q3IQQI',r))
x=adiff.graw(a,'Global/Latest'); y=adiff.graw(b,'Global/Latest')
print('Latest',len(x),len(y))
for o in adiff.ops(x,y): 
    i0,i1,j0,j1=o; print('  ',o,x[i0:(i1 or i0+8)].hex()[:50],'=>',y[j0:(j1 or j0+8)].hex()[:160])
def J(f):
    c=cfb.CFB(open(f,'rb').read())
    for sn,e in c.streams().items():
        if sn.startswith('Partitions/'): p=wlpart.Partition(rvtw.Stream(e.data)); return b''.join(bytes(m['raw']) for m in p.mem)
ja=J(a); jb=J(b); print('partition',len(ja),len(jb))
for o in adiff.ops(ja,jb,win=64,maxda=3000,maxdb=3000):
    i0,i1,j0,j1=o; print('  op',o,'ins' if i0==i1 else 'chg', (j1-j0) if j1 else '', jb[j0:j0+60].hex() if j1 else '')
