import sys,os,struct; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
os.environ['RVT_GEOM']='1'
import wlrec, wlpatch
src,dst=sys.argv[1],sys.argv[2]; WHICH=sys.argv[3]
m=wlrec.Model(src); pa=wlpatch.Patcher(m)
for pn,i,r,log,q in m.find(1046264):
    first=True
    for l in log:
        if WHICH in ("lvl","both") and l[1]=="FamilyElemRef.m_elemId" and first:
            pa.set(pn,l[2],struct.pack('<I',1351691),'base level 245423 -> 1351691'); first=False
        if WHICH in ('all',) and l[1]=='Element.m_assocLevelId':
            pa.set(pn,l[2],struct.pack('<I',1351691),'assocLevel -> 1351691')
        if WHICH in ('all',) and l[1]=='FamilyElemRef.m_elemId' and first:
            pa.set(pn,l[2],struct.pack('<I',1351691),'base level'); first=False
        if WHICH in ('all','off','both') and l[1]=='FamilyLevelRef.m_offset' and l[2]==3313656:
            pa.set(pn,l[2],struct.pack('<d',-0.5),'base offset')
        if WHICH in ("off_","both") and l[1]=="FamilyLevelRef.m_offset" and l[2]==3313656:
            pa.set(pn,l[2],struct.pack('<d',float(sys.argv[4]) if len(sys.argv)>4 else -0.5),'base offset')
print(pa.log); print('members touched',pa.save(dst))
