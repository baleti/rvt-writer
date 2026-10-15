import sys,os,struct,json; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,genlib,genlib2
seed=os.path.expanduser('~/rvt-research/rosetta/2024_floors12_base.rte'); out=sys.argv[1]
g=rvtgen.Gen(seed); ids8=[301553,301554,301555,301556,301557,301558,301559]; 
import wledit
# group 0 = first 7 + the c4 line = first id after the 84 (301637)
allnew=sorted(set(g.e.m.ids)-set(wledit.Editor(os.path.expanduser('~/rvt-research/write-lab/files/ds0.rte')).m.ids))
ids8=allnew[:7]+[allnew[84]]
FT=genlib2.FloorTpl(g,ids8)
et=g._et(); n=struct.unpack_from('<I',et,2)[0]
best=max(range(n),key=lambda k:(struct.unpack_from('<I',et,6+40*k+12)[0],struct.unpack_from('<I',et,6+40*k+8)[0]))
ea,eb,_=struct.unpack_from('<3I',et,6+40*best+8); tr=(ea,eb,eb)
rects=[(200,0,40,26),(260,0,17,9),(200,40,21,21),(230,40,50,12)]
man={'floors':[],'parts':[]}; fl_ids=[]
for (x0,y0,W,D) in rects:
    nids=[]
    for _ in range(8): nids.append(g.nextid); g.nextid+=1
    for hd,rec,it,nid,row in genlib2.make_floor(g,FT,nids,x0,y0,W,D):
        r=bytearray(row); struct.pack_into('<3I',r,8,*tr); g.new.append((hd,rec,it,nid)); g.rows.append(bytes(r))
    man['floors'].append([nids[2],x0,y0,W,D]); fl_ids.append(nids[2]); man['parts']+=[[i] for i in nids if i!=nids[2]]
REG=fl_ids
def _comp(raw):
    ops=genlib2.registry_ops(raw,ids8[2],REG)
    o=bytearray(raw)
    for pos,dl,ins in sorted(ops,key=lambda o:-o[0]): o[pos:pos+dl]=ins
    return bytes(o)
g.latest_edits=[('Latest',_comp)]
g.itag=FT.T['sp']['item'][16:18]; g.commit(out); json.dump(man,open(out+'.json','w')); print('wrote',out,len(rects))
