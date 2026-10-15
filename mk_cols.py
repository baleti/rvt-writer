import sys,os,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,genlib,genlib2
seed=os.path.expanduser('~/rvt-research/rosetta/2024_house_base.rte'); out=sys.argv[1]; NX,NY=int(sys.argv[2]),int(sys.argv[3])
g=rvtgen.Gen(seed); T=g.template(301563)
et=g._et(); n=struct.unpack_from('<I',et,2)[0]
best=max(range(n),key=lambda k:(struct.unpack_from('<I',et,6+40*k+12)[0],struct.unpack_from('<I',et,6+40*k+8)[0]))
ea,eb,_=struct.unpack_from('<3I',et,6+40*best+8); tr=(ea,eb,eb)
ids=[]
REG={301563:ids}
for i in range(NX):
    for j in range(NY):
        nid=g.nextid; g.nextid+=1
        hd,rec,it=genlib2.make_column(g,T,nid,10+i*8.0,5+j*8.0,0.0)
        g.new.append((hd,rec,it,nid)); g.rows.append(genlib._row(g,T,nid,8,tr)); ids.append(nid)
def _comp(raw,reg=REG):
    ops=[]
    for tid,ids in reg.items(): ops+=genlib2.registry_ops(raw,tid,ids)
    ops+=genlib2.registry_ops(raw,301553,REG[301563],must=301563)
    out=bytearray(raw)
    for pos,dl,ins in sorted(ops,key=lambda o:-o[0]): out[pos:pos+dl]=ins
    return bytes(out)
g.latest_edits=[('Latest',_comp)]
g.itag=T['item'][16:18]
g.commit(out)
import json; json.dump({'columns':[[i,10+k//NY*8.0,5+k%NY*8.0] for k,i in enumerate(ids)]},open(out+'.json','w'))
print('wrote',out,len(ids))
