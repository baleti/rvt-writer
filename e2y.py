import sys,struct,os; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import wledit
src,dst,eid,z=sys.argv[1],sys.argv[2],int(sys.argv[3]),float(sys.argv[4])
e=wledit.Editor(src); pn,i,r,log,q=e.trace(eid); b=e.m.parts[pn]['joined']
eds=[]
for l in log:
    if l[1]=='Plane.m_origin':
        x,y,_=struct.unpack_from('<3d',b,l[2]); eds.append((l[2],24,struct.pack('<3d',x,y,z)))
    if l[1]=='Level.m_isBuildingStory': eds.append((l[2],1,bytes([1-b[l[2]]])))
print(e.modify(eid,eds)); e.save(dst)
