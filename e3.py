import sys; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import wledit
e=wledit.Editor('files/orig2020.rvt'); new='FOUNDATION-2700-EXTENDED-NAME'
e.set_string(1351711,'DBView.m_viewName',new); e.set_string(1351691,'DatumPlane.m_text',new); e.save(sys.argv[1])
