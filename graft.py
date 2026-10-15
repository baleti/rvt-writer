"""bisect helper: base (Revit-saved) + donor's (Revit-saved base+1 element) records and, selectively, donor's Global streams / plain streams"""
import sys,struct,os,zlib; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtgen,cfb,rvtw
base,donor,dst,nid=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]); take=sys.argv[5].split(',') if len(sys.argv)>5 else []
d=rvtgen.Gen(donor); T=d.template(nid)
g=rvtgen.Gen(base); W=g.W
g.new.append((T['hdr'],T['rec'],T['item'],nid)); g.rows.append(T['row'])
dc=cfb.CFB(open(donor,'rb').read())
def draw(n):
    P=rvtw.Stream(dc.streams()[n].data).payload; i0=P.find(rvtw.GZ); return zlib.decompressobj(-15).decompress(P[i0+10:])
if 'ElemTable' in take: g.skip_elemtable=True; g.e.global_edit('Global/ElemTable',lambda raw: draw('Global/ElemTable'))
g.nextid=nid+1
g.itag=T['item'][W+8:W+10]
edits=[]
for n in take:
    if n in ('History','DocumentIncrementTable','Latest'): g.e.global_edit('Global/'+n,lambda raw,n=n: draw('Global/'+n))
g.commit(dst)
c=cfb.CFB(open(dst,'rb').read())
dn=[n for n in dc.streams() if n.startswith('Partitions/')][0].split('/')[1]
for en in c.entries:
    if en.name.isdigit() and en.name!=dn and 'Partitions' in c.path(en):
        raw=bytearray(en.raw); nm=dn.encode('utf-16le')+b'\0\0'; raw[0:64]=nm+b'\0'*(64-len(nm)); en.raw=bytes(raw); en.name=dn
for n in take:
    if n in ('BasicFileInfo','Contents','ProjectInformation'): c.streams()[n].data=dc.streams()[n].data
cfb.write(c,dst)
print('ok')
