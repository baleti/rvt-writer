"""add ONE FillPatternElement to a seed (any year) through rvtgen (member-splitting insertion) - 2020 feasibility test"""
import sys,struct,os,argparse; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtgen,genlib
ap=argparse.ArgumentParser(); ap.add_argument('seed'); ap.add_argument('out'); ap.add_argument('--src',type=int,required=True); ap.add_argument('--name',default='WL pattern'); ap.add_argument('--n',type=int,default=1); ap.add_argument('--triple')
a=ap.parse_args()
g=rvtgen.Gen(a.seed); W=g.W; S=a.src; T=g.template(S); idS=struct.pack(g.IDF,S)
L={n:(o,e) for n,o,e,_ in T['log']}
et=g._et(); RW=g.RW; n_=struct.unpack_from('<I',et,2)[0]
best=max(range(n_),key=lambda k:(struct.unpack_from('<I',et,6+RW*k+12)[0],struct.unpack_from('<I',et,6+RW*k+8)[0]))
tr=struct.unpack_from('<3I',et,6+RW*best+8)
if a.triple: tr=tuple(int(x) for x in a.triple.split(','))
print('triple',tr)
new_ids=[]
for k in range(a.n):
    nid=g.nextid; g.nextid+=1; idN=struct.pack(g.IDF,nid); new_ids.append(nid)
    rec=bytearray(T['rec']); rec[4:4+W]=idN; rec[L['Element.m_id'][0]:L['Element.m_id'][1]]=idN
    nm=a.name+(str(k) if a.n>1 else ''); o,e=L['FillPattern.m_name']; rec[o:e]=genlib.ustr(nm)
    rec=g.stamp(bytes(rec))
    hdr=bytearray(T['hdr']); genlib.rep(hdr,idS,idN)
    item=bytearray(T['item']); genlib.rep(item,idS,idN)
    row=bytearray(T['row']); genlib.rep(row,idS,idN)
    struct.pack_into('<3I',row,8,*tr)
    g.new.append((bytes(hdr),rec,bytes(item),nid)); g.rows.append(bytes(row))
def reg(raw):
    LIM=1<<(31 if W==4 else 40); pos=raw.find(idS); p=pos
    while struct.unpack_from(g.IDF,raw,p-W)[0]<struct.unpack_from(g.IDF,raw,p)[0] and struct.unpack_from(g.IDF,raw,p-W)[0]<LIM: p-=W
    last=pos
    while struct.unpack_from(g.IDF,raw,last+W)[0]>struct.unpack_from(g.IDF,raw,last)[0] and struct.unpack_from(g.IDF,raw,last+W)[0]<LIM: last+=W
    cnt=struct.unpack_from('<I',raw,p-4)[0]; assert cnt==(last-p)//W+1,(cnt,(last-p)//W+1)
    out=bytearray(raw); out[last+W:last+W]=b''.join(struct.pack(g.IDF,i) for i in new_ids); struct.pack_into('<I',out,p-4,cnt+len(new_ids)); return bytes(out)
g.latest_edits=[('Latest',reg)]
g.itag=T['item'][W+8:W+10]
g.commit(a.out); print('ok',a.out)
