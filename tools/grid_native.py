#!/usr/bin/env python3
"""grid_native.py SEED NATIVEFILE OUT [nohist]: add Revit's OWN grid element (from NATIVEFILE, id = next id of SEED) through my writer, no modification"""
import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL)
import rvtgen,genlib2,genlib,scenes
seed,native,out=sys.argv[1:4]; genlib2.YEAR=2026
g=rvtgen.Gen(seed); gn=rvtgen.Gen(native); tid=min(set(gn.e.m.ids)-set(g.e.m.ids)); T=gn.template(tid)
tr=tuple(int.from_bytes(T['row'][8+4*k:12+4*k],'little') for k in range(3)); print('native tid',tid,'triple',tr)
nid=g.nextid; assert nid==tid; g.nextid+=1
if os.environ.get('MOVEGCS'):
    tg=g.template(76368); g.delete(76368); g.new.append((tg['hdr'],tg['rec'],tg['item'],76368))
g.new.append((T['hdr'],g.stamp(T['rec']),T['item'],nid)); g.rows.append(T['row'])
g.itag=T['item'][16:18]
g.latest_edits=[('Latest',lambda raw:genlib2.set_last_grid_name(genlib2.grid_registry(raw,genlib2.grid_anchors(2026),[nid]),'G2'))] if not os.environ.get('NOLATEST') else []
import adiff
if len(sys.argv)>4:
    for st in sys.argv[4].split(','):
        nr=adiff.graw(native,st); g.e.global_edit(st,lambda raw,nr=nr: nr)
if os.environ.get('SKIPET'): g.skip_elemtable=True
g.commit(out); print('wrote',out)
if os.environ.get('FIXROW'):
    import struct as _s, wledit
    def fixrow(raw):
        o2=bytearray(raw); n=_s.unpack_from('<I',o2,2)[0]
        for k in range(n):
            o=6+40*k
            if int.from_bytes(o2[o:o+8],'little')==76368: _s.pack_into('<I',o2,o+12,522)
        return bytes(o2)
    e2=wledit.Editor(out); e2.global_edit('Global/ElemTable',fixrow); e2.save(out+'.fix'); os.replace(out+'.fix',out); print('row fixed')

if os.environ.get('RAW'):
    import wledit
    e3=wledit.Editor(out); ns=wledit.Editor(native).m.c.streams()
    for nm in os.environ['RAW'].split(','): e3.m.c.streams()[nm].data=ns[nm].data
    e3.save(out+'.raw'); os.replace(out+'.raw',out); print('raw streams',os.environ['RAW'])

if os.environ.get('RENAME'):
    import wledit
    e4=wledit.Editor(out); c=e4.m.c; old,new=os.environ['RENAME'].split(':'); pp=c._paths()
    for en in c.entries:
        if en.idx in pp and pp[en.idx].lstrip('/')==old: nm=new.split('/')[-1]; assert len(nm)==len(en.name); en.name=nm; r=bytearray(en.raw); r[:2*len(nm)]=nm.encode('utf-16le'); en.raw=bytes(r); print('renamed',old,'->',new)
    c._pp=None
    e4.save(out+'.rn'); os.replace(out+'.rn',out)
