import sys,struct,os; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
os.environ['RVT_GEOM']='1'
import wledit,wlrec
src,dst,srcid=sys.argv[1],sys.argv[2],int(sys.argv[3])      # srcid: existing element whose ElemTable row is copied and after whose record we insert
donor='files/ds3.rte'; did=301553
mb=wlrec.Model(donor); pn,i,r,log,q=list(mb.find(did))[0]; rec=bytearray(mb.parts[pn]['joined'][i:q])
e=wledit.Editor(src); W=e.m.IDW; hs=12+W
pn2,i2,r2,log2,q2=e.trace(srcid); pt=e.part(pn2); b=e.m.parts[pn2]['joined']
oldL=struct.unpack_from('<I',b,i2+4+W+4)[0]
struct.pack_into('<I',rec,0,oldL)
k=pt.replace(q2,4,bytes(rec)+struct.pack('<I',len(rec)-hs)); pt.mem[k]['dx1']=1
def fn(raw):
    n=struct.unpack_from('<I',raw,2)[0]; RW=40
    rows=raw[6:]; body=bytearray(rows[:n*RW]); srcrow=None
    for kk in range(n):
        r=rows[kk*RW:(kk+1)*RW]
        if struct.unpack_from('<Q',r,0)[0]==srcid: srcrow=bytearray(r)
    nr=srcrow
    nr[0:8]=did.to_bytes(8,'little'); nr[20:28]=did.to_bytes(8,'little')
    body+=nr; out=bytearray(raw[:6]); struct.pack_into('<I',out,2,n+1); out+=body+rows[n*RW:]
    if os.environ.get('COUNTER'):
        t=len(out)-24; c=struct.unpack_from('<I',out,t+16)[0]; struct.pack_into('<I',out,t+16,did+1)
    return bytes(out)
e.global_edit('Global/ElemTable',fn); e.save(dst)
