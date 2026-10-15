import sys,os,struct,json; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,genlib,genlib2
seed=os.path.expanduser('~/rvt-research/rosetta/2024_house_base.rte'); out=sys.argv[1]; NW=int(sys.argv[2]); ND=int(sys.argv[3])
g=rvtgen.Gen(seed); TW=g.template(301560); TD=g.template(301558)
et=g._et(); n=struct.unpack_from('<I',et,2)[0]
best=max(range(n),key=lambda k:(struct.unpack_from('<I',et,6+40*k+12)[0],struct.unpack_from('<I',et,6+40*k+8)[0]))
ea,eb,_=struct.unpack_from('<3I',et,6+40*best+8); tr=(ea,eb,eb)
man={'windows':[],'doors':[]}
REG={301560:[],301558:[]}
for k in range(NW):
    nid=g.nextid; g.nextid+=1; x=14.0+k*2.5
    hd,rec,it=genlib2.make_hosted_x(g,TW,nid,x); g.new.append((hd,rec,it,nid)); g.rows.append(genlib._row(g,TW,nid,8,tr)); man['windows'].append([nid,x,0.0]); REG[301560].append(nid)
for k in range(ND):
    nid=g.nextid; g.nextid+=1; x=32.0+k*3.5
    hd,rec,it=genlib2.make_hosted_x(g,TD,nid,x); g.new.append((hd,rec,it,nid)); g.rows.append(genlib._row(g,TD,nid,8,tr)); man['doors'].append([nid,x,0.0]); REG[301558].append(nid)
def _comp(raw,reg=REG):
    ops=[]
    for tid,ids in reg.items(): ops+=genlib2.registry_ops(raw,tid,ids)
    out=bytearray(raw)
    for pos,dl,ins in sorted(ops,key=lambda o:-o[0]): out[pos:pos+dl]=ins
    return bytes(out)
g.latest_edits=[('Latest',_comp)]
g.add_deletion_children(301553,[m[0] for m in man['windows']+man['doors']])
g.itag=TW['item'][16:18]; g.commit(out); json.dump(man,open(out+'.json','w')); print('wrote',out,NW,ND)
