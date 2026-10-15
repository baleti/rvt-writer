import sys,os,struct; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
os.environ['RVT_GEOM']='1'
import wlrec, wlpatch
src,dst,eid=sys.argv[1],sys.argv[2],int(sys.argv[3]); newz=float(sys.argv[4])
m=wlrec.Model(src); pa=wlpatch.Patcher(m)
for pn,i,r,log,q in m.find(eid):
    for l in log:
        if l[1]=='Plane.m_origin':
            old=struct.unpack_from('<3d',m.parts[pn]['joined'],l[2])
            nb=struct.pack('<3d',old[0],old[1],newz); pa.set(pn,l[2],nb,'origin z %r -> %r'%(old[2],newz))
        if l[1]=='Level.m_isBuildingStory':
            b=m.parts[pn]['joined'][l[2]]; pa.set(pn,l[2],bytes([1-b]),'isBuildingStory %d -> %d'%(b,1-b))
print(pa.log); print('members touched',pa.save(dst))
