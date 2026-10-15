import sys,struct,os; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
os.environ['RVT_GEOM']='1'
import wledit
e=wledit.Editor('files/orig2024.rte'); W=e.m.IDW; hs=12+W
mv=281158; anchor=5855
pn,i,r,log,q=e.trace(mv); pt=e.part(pn); b=e.m.parts[pn]['joined']
rec=bytearray(b[i:q]); A_mv=bytes(b[i:i+4])
pn2,i2,r2,log2,q2=e.trace(anchor)
assert q2<i
print('anchor',i2,q2,'moved',i,q)
# 1) delete moved record (later offset)
k=pt.replace(i,(q-i)+4,A_mv); pt.mem[k]['dx1']=pt.mem[k].get('dx1',0)-1
# 2) insert after anchor
oldL=struct.unpack_from('<I',b,i2+4+W+4)[0]
struct.pack_into('<I',rec,0,oldL)
k2=pt.replace(q2,4,bytes(rec)+struct.pack('<I',len(rec)-hs)); pt.mem[k2]['dx1']=pt.mem[k2].get('dx1',0)+1
print(k,k2)
e.save('files/e8_move_2024.rte')
