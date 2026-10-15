"""gen_delete.py SEED OUT ID[,ID..] [--fill]  delete elements completely (header, record, zone records, ElemTable row); --fill also removes the ids from the FillPattern registry in Latest"""
import sys,struct,json; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtgen
seed,out,ids=sys.argv[1],sys.argv[2],[int(x) for x in sys.argv[3].split(',')]; fill='--fill' in sys.argv
g=rvtgen.Gen(seed); W=g.W
for i in ids: g.delete(i)
if fill:
    def reg(raw):
        LIM=1<<(31 if W==4 else 40); out=bytearray(raw)
        for tid in ids:
            idb=struct.pack(g.IDF,tid); pos=out.find(idb); p=pos
            while struct.unpack_from(g.IDF,out,p-W)[0]<struct.unpack_from(g.IDF,out,p)[0] and struct.unpack_from(g.IDF,out,p-W)[0]<LIM: p-=W
            cnt=struct.unpack_from('<I',out,p-4)[0]; del out[pos:pos+W]; struct.pack_into('<I',out,p-4,cnt-1)
        return bytes(out)
    g.latest_edits=[('Latest',reg)]
g.commit(out); json.dump({'deleted':ids},open(out+'.json','w')); print('deleted',ids)
