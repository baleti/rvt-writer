#!/usr/bin/env python3
"""gen_levels.py - add N generated Levels (elevations from a formula, names L01..) to a Revit-saved 2024 .rte (seed ds0.rte) with my own writer.
Latest registries (6 per-level tables, structure learnt from Revit's own lv1/lv2/lv3 saves) + partition (header, record, dummy zone record per level) + ElemTable."""
import sys,struct,math,argparse,json,os,zlib; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtgen,wledit,rvtw
def elevations(kind,n,step,start):
    phi=(1+5**.5)/2
    if kind=='linear': return [start+step*i for i in range(n)]
    if kind=='golden': return [start+step*(phi**(i/3.0)-1) for i in range(n)]
    if kind=='sine': return [start+step*i+step*0.8*math.sin(i*0.6) for i in range(n)]
    if kind=='setback': return [start+step*i*(1+0.02*i) for i in range(n)]
LATEST_OFFS={2024:(85623,85675,87121,87261,87317,88812,88984,89156),2026:(86374,86426,87872,88012,88068,89631,89803,89975)}
def latest_patch(raw,ids,year=2024,as_ops=False,O=None):
    O=O or LATEST_OFFS[year]
    N=len(ids); out=bytearray(raw); P=lambda i:struct.pack('<Q',i)
    E=lambda i: P(i)+struct.pack('<I',1)+struct.pack('<2d',9.0,9.0)
    def chk(pos,b): assert bytes(raw[pos:pos+len(b)])==b,(pos,bytes(raw[pos:pos+len(b)]).hex(),b.hex())
    # (offset in the seed, deleted bytes, inserted bytes) - all from the original; applied from the end to the start
    chk(O[0],b'\x06'); chk(O[2],b'\x06'); chk(O[3],bytes.fromhex('0100000006')); chk(O[5],b'\x06'); chk(O[6],b'\x06'); chk(O[7],bytes(8))
    ops=[(O[7],8,b''.join(E(i) for i in ids)+struct.pack('<I',N)+b''.join(E(i) for i in ids)+struct.pack('<I',N)+b''.join(E(i) for i in ids)),
         (O[6],1,b''.join(E(i) for i in ids)+bytes([6+N])),
         (O[5],1,bytes([6+N])),
         (O[4],0,b''.join(P(i) for i in ids)),
         (O[3],5,b''.join(P(i)+bytes(4) for i in ids)+bytes.fromhex('01000000')+bytes([6+N])),
         (O[2],1,bytes([6+N])),
         (O[1],0,b''.join(P(i) for i in ids)),
         (O[0],1,bytes([6+N]))]
    if as_ops: return ops
    for pos,dl,ins in ops: out[pos:pos+dl]=ins
    return bytes(out)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seed',default='files/ds0.rte'); ap.add_argument('--template',default='files/ds3b.rte'); ap.add_argument('--tid',type=int,default=301553)
    ap.add_argument('--n',type=int,default=30); ap.add_argument('--kind',default='golden',choices=['linear','golden','sine','setback']); ap.add_argument('--step',type=float,default=12.0); ap.add_argument('--start',type=float,default=40.0)
    ap.add_argument('--prefix',default='L'); ap.add_argument('--out',required=True)
    a=ap.parse_args()
    T=rvtgen.Gen(a.template).template(a.tid); W=8
    g=rvtgen.Gen(a.seed); g.itag=T['item'][W+8:W+10]
    L={n:(o,z) for n,o,z,_ in T['log']}
    elev=elevations(a.kind,a.n,a.step,a.start); man=[]
    for k,z in enumerate(elev):
        nid=g.nextid; g.nextid+=1; idb=struct.pack('<Q',nid); name='%s%02d'%(a.prefix,k+1)
        rec=bytearray(T['rec']); rec[4:12]=idb; rec[L['Element.m_id'][0]:L['Element.m_id'][1]]=idb
        # name (string field, length may differ): rebuild record around it
        so,se=L['DatumPlane.m_text']; nb=struct.pack('<I',len(name))+name.encode('utf-16le')
        # z of both Plane.m_origin occurrences: patch before resizing
        for (n_,o,zz,_) in T['log']:
            if n_=='Plane.m_origin': x,y,_z=struct.unpack_from('<3d',rec,o); struct.pack_into('<3d',rec,o,x,y,z)
        rec[so:se]=nb
        rec=bytearray(g.stamp(bytes(rec)))
        hdr=bytearray(T['hdr']); hdr[0:W]=idb
        hl={n:(o,zz) for n,o,zz,_ in T['hlog']}
        d_end=hl['ElementParents.m_deletion'][1]; hdr[d_end-W:d_end]=idb
        item=bytearray(T['item']); item[0:W]=idb
        row=bytearray(T['row']); row[0:8]=idb; row[20:28]=idb
        g.new.append((bytes(hdr),bytes(rec),bytes(item),nid)); g.rows.append(bytes(row)); man.append((nid,name,z))
    et=g._et(); n_=struct.unpack_from('<I',et,2)[0]
    best=max(range(n_),key=lambda k:(struct.unpack_from('<I',et,6+40*k+12)[0],struct.unpack_from('<I',et,6+40*k+8)[0]))
    ea,eb,_=struct.unpack_from('<3I',et,6+40*best+8)
    for i in range(len(g.rows)):
        r=bytearray(g.rows[i]); struct.pack_into('<3I',r,8,ea,eb,eb); g.rows[i]=bytes(r)
    ids=[m[0] for m in man]
    g.latest_edits=[('Latest',lambda raw: latest_patch(raw,ids))]
    g.commit(a.out); json.dump(man,open(a.out+'.json','w')); print('generated',len(man),'levels ->',a.out)
if __name__=="__main__": main()
