import sys,struct,zlib,os; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import wledit,rvtw
src,dst,srcid=sys.argv[1],sys.argv[2],int(sys.argv[3])
e=wledit.Editor(src); W=e.m.IDW
new=int(os.environ.get('NEWID',max(e.m.ids)+1))
name='Level added by write-lab'
def setz(b):
    x,y,z=struct.unpack('<3d',b); return struct.pack('<3d',x,y,66.0)
def setname(b): return struct.pack('<I',len(name))+name.encode('utf-16le')
MODE=os.environ.get('MODE','full')
FP=os.environ.get('FP')
fe=[('FillPattern.m_name',0,setname)] if FP else [('DatumPlane.m_text',0,setname),('Plane.m_origin',0,setz),('Plane.m_origin',1,setz)] if MODE=='full' else []
if FP: fe=[('FillPattern.m_name',0,setname)]
print('new id',new,e.clone(srcid,new,fe))
e.part(list(e.parts)[0]).hdr_dn=1
def fn(raw):
    n=struct.unpack_from('<I',raw,2)[0]; RW=28 if W==4 else 40
    rows=raw[6:]; out=bytearray(raw[:6]); body=bytearray()
    srcrow=None
    for k in range(n):
        r=rows[k*RW:(k+1)*RW]
        if int.from_bytes(r[:W],'little')==srcid: srcrow=bytearray(r)
        body+=r
    nr=bytearray(srcrow)
    for off in range(0,RW-W+1,4):
        pass
    for off in (0,16 if W==4 else 20):
        if int.from_bytes(nr[off:off+W],'little')==srcid: nr[off:off+W]=new.to_bytes(W,'little')
    assert max(int.from_bytes(rows[k*RW:k*RW+W],'little') for k in range(n))<new
    body+=nr
    struct.pack_into('<I',out,2,n+1); out+=body+rows[n*RW:]
    if os.environ.get('COUNTER'): struct.pack_into('<I',out,len(out)-12,new+1)
    return bytes(out)
e.global_edit('Global/ElemTable',fn)
if os.environ.get('REG'):
    def reg(raw):
        last=int(os.environ['REG']); pos=raw.find(struct.pack('<Q',last)); n=struct.unpack_from('<I',raw,pos-8*0-0)[0] if False else None
        # count lies 4 bytes before the first id; walk back while ids ascending
        p=pos
        while struct.unpack_from('<Q',raw,p-8)[0]<struct.unpack_from('<Q',raw,p)[0] and struct.unpack_from('<Q',raw,p-8)[0]<1<<40: p-=8
        cnt=struct.unpack_from('<I',raw,p-4)[0]; nids=(pos-p)//8+1
        assert cnt==nids,(cnt,nids)
        out=bytearray(raw); out[pos+8:pos+8]=struct.pack('<Q',new); struct.pack_into('<I',out,p-4,cnt+1)
        return bytes(out)
    e.global_edit('Global/Latest',reg)
e.save(dst)
