import sys,struct; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import wledit
src,dst,eid=sys.argv[1],sys.argv[2],int(sys.argv[3])
e=wledit.Editor(src); W=4+4*0
print(e.delete(eid))
def fn(raw):
    n=struct.unpack_from('<I',raw,2)[0]; W=28 if e.m.IDW==4 else 40
    keep=bytearray(); rows=raw[6:]
    for k in range(n):
        r=rows[k*W:(k+1)*W]
        if int.from_bytes(r[:e.m.IDW],'little')!=eid: keep+=r
    assert len(keep)==(n-1)*W
    out=bytearray(raw[:6]); struct.pack_into('<I',out,2,n-1); out+=keep+rows[n*W:]
    return bytes(out)
e.global_edit('Global/ElemTable',fn); e.save(dst)
