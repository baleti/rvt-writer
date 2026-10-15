import sys,struct,os,zlib; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
os.environ['RVT_GEOM']='1'
import wledit,wlrec,rvtw,cfb,wlpart
base,donor,dst=sys.argv[1:4]; MODE=os.environ.get('MODE','graft'); S=281158; N=301553
def joined(f):
    c=cfb.CFB(open(f,'rb').read())
    for sn,e in c.streams().items():
        if sn.startswith('Partitions/'): 
            p=wlpart.Partition(rvtw.Stream(e.data)); return sn,p,b''.join(bytes(m['raw']) for m in p.mem)
dn,dp,dj=joined(donor)
e=wledit.Editor(base); pn=list(e.m.parts)[0]; pt=e.part(pn); bj=e.m.parts[pn]['joined']; W=8; hs=20
# --- oracle pieces from donor ---
hdr_item=dj[0:131]                   # [id][L][tag..body] of new ElementHeader (without A)
Lh=struct.unpack_from('<I',hdr_item,8)[0]
# element record in donor
dm=wlrec.Model(donor); r=list(dm.find(N))[0]; rec=bytes(dm.parts[r[0]]['joined'][r[1]:r[4]])
# item3: 22 bytes with id N
it=[k for k in range(len(dj)-22) if dj[k:k+8]==struct.pack('<Q',N) and dj[k+8:k+12]==bytes.fromhex('8f001001')][0]
item3=dj[it:it+22]
print('hdr',len(hdr_item),'rec',len(rec),'item',item3.hex())
# --- insert into base (descending offsets): item3 after S's item, record after S's record, header at start ---
def prevL_at(q,hs_):   # A of the record starting at q = L of previous record
    return struct.unpack_from('<I',bj,q)[0]
q_item=int(os.environ.get('QI','6372611')); q_rec=int(os.environ.get('QR','890331'))
# item3 record: A (copy of old next's A) + 18 bytes ; next A := its L (2)
k3=pt.replace(q_item+4,0,item3[:18]+struct.pack('<I',2)); pt.mem[k3]['dx1']=pt.mem[k3].get('dx1',0)+1
k=pt.replace(q_rec+4,0,bytes(rec[4:])+struct.pack('<I',len(rec)-hs)); pt.mem[k]['dx1']=pt.mem[k].get('dx1',0)+1
k0=pt.replace(0,0,hdr_item+struct.pack('<I',Lh)); pt.mem[k0]['dx1']=pt.mem[k0].get('dx1',0)+1
pt.hdr_dn=1
if os.environ.get('GAPS','1')=='1':
    for kk,(g,h) in enumerate(zip(pt.gaps,dp.gaps)):
        if len(g)==220 and len(h)==220: g[28:]=h[28:]
    pt.tail=dp.tail
pt.rechunk_header_region()
def draw(n):
    P=rvtw.Stream(dp.st.payload if False else cfb.CFB(open(donor,'rb').read()).streams()[n].data).payload; i0=P.find(rvtw.GZ); return zlib.decompressobj(-15).decompress(P[i0+10:])
for n in ('ElemTable','History','DocumentIncrementTable','Latest'):
    e.global_edit('Global/'+n,lambda raw,n=n: draw('Global/'+n))
if os.environ.get('PLAIN','1')=='1':
    dc=cfb.CFB(open(donor,'rb').read())
    for n in ('BasicFileInfo','Contents','ProjectInformation','TransmissionData','Global/PartitionTable','Global/ContentDocuments'):
        e.m.c.streams()[n].data=dc.streams()[n].data
if os.environ.get('RENAME'):
    for en in e.m.c.entries:
        if en.name==os.environ['RENAME_FROM']:
            nm=os.environ['RENAME'].encode('utf-16le')+b'\0\0'; raw=bytearray(en.raw); raw[0:64]=nm+b'\0'*(64-len(nm)); en.raw=bytes(raw); en.name=os.environ['RENAME']
e.save(dst)
