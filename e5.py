import sys,struct; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import wledit
e=wledit.Editor('files/orig2020.rvt')
pn,i,r,log,q=e.trace(857191)
st=[l for l in log if l[1]=='ParamValueSetAString.m_paramSet'][0][2]
txt='Added by write-lab'
entry=struct.pack('<I',(-1010106)&0xffffffff)+struct.pack('<I',len(txt))+txt.encode('utf-16le')
print(e.modify(857191,[(st,4,struct.pack('<I',3)),(st+4,0,entry)]))
e.save('files/e5_2020.rvt')
