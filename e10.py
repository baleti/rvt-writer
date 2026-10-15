"""add ONE FillPatternElement (clone of S) to a 2024 .rte written by Revit (ds0), generating every piece myself (no donor bytes)"""
import sys,struct,os,zlib; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
os.environ['RVT_GEOM']='1'
import wledit,wlrec,rvtw,cfb,wlpart
base,dst=sys.argv[1:3]; S=int(os.environ.get('SRC','281158')); NAME=os.environ.get('NAME','WL pattern')
e=wledit.Editor(base); pn=list(e.m.parts)[0]; pt=e.part(pn); bj=e.m.parts[pn]['joined']; W=e.m.IDW; hs=12+W; hsh=4+W+4; IDF='<I' if W==4 else '<Q'; RW=28 if W==4 else 40; CTR=8 if W==4 else 12
N=max(e.m.ids)+1 if not os.environ.get('NEWID') else int(os.environ['NEWID'])
# counter in ElemTable tail
def et_raw():
    c=e.m.c; P=rvtw.Stream(c.streams()['Global/ElemTable'].data).payload; i=P.find(rvtw.GZ); return zlib.decompressobj(-15).decompress(P[i+10:])
er=et_raw(); counter=struct.unpack_from('<I',er,len(er)-CTR)[0]
if not os.environ.get('NEWID'): N=counter+1
print('new id',N,'counter',counter)
idS=struct.pack(IDF,S); idN=struct.pack(IDF,N)
# ---- locate S pieces in the base partition
pn2,i2,r2,log2,q2=e.trace(S); recS=bytearray(bj[i2:q2])
# header of S: id at k with L field then tag 0x59f
EHT=struct.pack('<H',e.m.sch.by['ElementHeader']+12)
hk=[k for k in range(len(bj)-20) if bj[k:k+W]==idS and bj[k+W+4:k+W+6]==EHT][0]
Lh=struct.unpack_from('<I',bj,hk+W)[0]; hdrS=bytearray(bj[hk:hk+W+4+Lh])
hdrN=bytearray(hdrS); 
off=0
while True:
    off=hdrN.find(idS,off)
    if off<0: break
    hdrN[off:off+8]=idN; off+=8
sit=[k for k in range(len(bj)-22) if bj[k:k+W]==idS and bj[k+W+4:k+W+8]==bytes.fromhex('02000000')][0]
pat=bytes(bj[sit+W:sit+W+4]); itag=bytes(bj[sit+W+8:sit+W+10])
itemN=bytearray(bj[sit:sit+W+10]); itemN[0:W]=idN
print('hdr',len(hdrN),'rec',len(recS),'item',itemN.hex())
# ---- new element record: clone with new name
import zlib as _z
recN=bytearray(recS); recN[4:4+W]=idN
for l in log2:
    if l[1]=='Element.m_id': recN[l[2]-i2:l[3]-i2]=idN
ent=[l for l in log2 if l[1]=='FillPattern.m_name'][0]
a,z=ent[2]-i2,ent[3]-i2; recN[a:z]=struct.pack('<I',len(NAME))+NAME.encode('utf-16le')
struct.pack_into('<I',recN,4+W+4,len(recN)-hs); struct.pack_into('<I',recN,4+W,_z.adler32(bytes(recN[4+W+8:]))&0xffffffff)
# ---- positions: item3 table start & record region start taken as in Revit's own add: right after the existing run heads
# record: first among element records = right after the A of the first element record (= end of header chain)
offs_=pt.offs(); first20=[k for k,m in enumerate(pt.mem) if m['hs']==hs][0]
q_rec=offs_[first20]-4          # A of the first element record (end of the header chain)
sit0=min(k for k in range(8,len(bj)-22) if bj[k+W+4:k+W+8]==bytes.fromhex('02000000') and bj[k+W+8:k+W+10]==itag and struct.unpack_from(IDF,bj,k)[0] in e.m.ids)
q_item=sit0-4
print('q_rec',q_rec,'q_item',q_item)
if not os.environ.get('SKIP_ITEM'): k3=pt.replace(q_item+4,0,bytes(itemN)+struct.pack('<I',2)); pt.mem[k3]['dx1']=pt.mem[k3].get('dx1',0)+1
k=pt.replace(q_rec+4,0,bytes(recN[4:])+struct.pack('<I',len(recN)-hs)); pt.mem[k]['dx1']=pt.mem[k].get('dx1',0)+1
k0=pt.replace(0,0,bytes(hdrN)+struct.pack('<I',Lh)); pt.mem[k0]['dx1']=pt.mem[k0].get('dx1',0)+1
pt.hdr_dn=1
pt.rechunk_header_region(hsh)
# ---- ElemTable
EP=int(os.environ.get('EP','0')); M1=int(os.environ.get('M1','0')); M2=None
def fn(raw):
    global EP,M1,M2
    n=struct.unpack_from('<I',raw,2)[0]; rows=raw[6:]
    best=max(range(n),key=lambda k:(struct.unpack_from('<I',rows,RW*k+12)[0],struct.unpack_from('<I',rows,RW*k+8)[0]))
    if os.environ.get('ROWFROMS'):
        ks=[k for k in range(n) if int.from_bytes(rows[RW*k:RW*k+W],'little')==S][0]; EP,M1,M2=struct.unpack_from('<3I',rows,RW*ks+8)
    elif not os.environ.get('EP'): EP=struct.unpack_from('<I',rows,RW*best+8)[0]; M1=struct.unpack_from('<I',rows,RW*best+12)[0]
    print('row fields',EP,M1)
    row=bytearray(RW)
    if W==8:
        struct.pack_into('<Q',row,0,N); struct.pack_into('<3I',row,8,EP,M1,M2 if M2 is not None else M1); struct.pack_into('<Q',row,20,N); row[28:36]=b'\xff'*8
    else:
        struct.pack_into('<II',row,0,N,N); struct.pack_into('<3I',row,8,EP,M1,M2 if M2 is not None else M1); row[24:28]=b'\xff'*4
    out=bytearray(raw[:6]); struct.pack_into('<I',out,2,n+1); out+=rows[:n*RW]+row+rows[n*RW:]
    struct.pack_into('<I',out,len(out)-CTR,N)
    return bytes(out)
e.global_edit('Global/ElemTable',fn)
# ---- Latest registry for FillPatternElements
def reg(raw):
    pos=raw.find(idS); p=pos; LIM=1<<(31 if W==4 else 40)
    while struct.unpack_from(IDF,raw,p-W)[0]<struct.unpack_from(IDF,raw,p)[0] and struct.unpack_from(IDF,raw,p-W)[0]<LIM: p-=W
    last=pos
    while struct.unpack_from(IDF,raw,last+W)[0]>struct.unpack_from(IDF,raw,last)[0] and struct.unpack_from(IDF,raw,last+W)[0]<LIM: last+=W
    cnt=struct.unpack_from('<I',raw,p-4)[0]; assert cnt==(last-p)//W+1,(cnt,(last-p)//W+1)
    assert struct.unpack_from(IDF,raw,last)[0]<N
    out=bytearray(raw); out[last+W:last+W]=idN; struct.pack_into('<I',out,p-4,cnt+1); return bytes(out)
if not os.environ.get('SKIP_REG'): e.global_edit('Global/Latest',reg)
e.save(dst)
