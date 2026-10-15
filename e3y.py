import sys; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import wledit
src,dst,eid,new=sys.argv[1:5]
e=wledit.Editor(src); print(e.set_string(int(eid),'DatumPlane.m_text',new)); e.save(dst)
