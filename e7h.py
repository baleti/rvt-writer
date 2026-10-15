import sys,struct,os,zlib; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
os.environ['RVT_GEOM']='1'
import wledit,wlrec,rvtw,cfb
src,dst,srcid=sys.argv[1],sys.argv[2],int(sys.argv[3]); which=sys.argv[4].split(',')   # which globals to take from donor: History,DocumentIncrementTable,Latest
donor=os.environ.get('DONOR','files/ds3.rte'); did=301553
mb=wlrec.Model(donor); pn,i,r,log,q=list(mb.find(did))[0]; rec=bytearray(mb.parts[pn]['joined'][i:q])
dc=mb.c
def draw(n):
    P=rvtw.Stream(dc.streams()[n].data).payload; i0=P.find(rvtw.GZ); return zlib.decompressobj(-15).decompress(P[i0+10:])
e=wledit.Editor(src); W=e.m.IDW; hs=12+W
pn2,i2,r2,log2,q2=e.trace(srcid); pt=e.part(pn2); b=e.m.parts[pn2]['joined']
struct.pack_into('<I',rec,0,struct.unpack_from('<I',b,i2+4+W+4)[0])
k=pt.replace(q2,4,bytes(rec)+struct.pack('<I',len(rec)-hs)); pt.mem[k]['dx1']=1
drow=draw('Global/ElemTable'); nd=struct.unpack_from('<I',drow,2)[0]
newrow=[drow[6+40*kk:6+40*kk+40] for kk in range(nd) if struct.unpack_from('<Q',drow,6+40*kk)[0]==did][0]
def fn(raw):
    n=struct.unpack_from('<I',raw,2)[0]; rows=raw[6:]
    out=bytearray(raw[:6]); struct.pack_into('<I',out,2,n+1); out+=rows[:n*40]+newrow+rows[n*40:]
    struct.pack_into('<I',out,len(out)-12,did+1)
    return bytes(out)
pt.hdr_dn=1
if os.environ.get('ELEMFULL'): fn=lambda raw: draw('Global/ElemTable')
e.global_edit('Global/ElemTable',fn)
for n in which:
    if n: e.global_edit('Global/'+n,lambda raw,n=n: draw('Global/'+n))
if os.environ.get('RENAME'):
    for en in e.m.c.entries:
        if en.name==os.environ.get('RENAME_FROM','59'):
            nm=os.environ.get('RENAME','60').encode('utf-16le')+b'\0\0'; raw=bytearray(en.raw); raw[0:64]=nm+b'\0'*(64-len(nm)); en.raw=bytes(raw); en.name=os.environ.get('RENAME','60')
e.save(dst)
