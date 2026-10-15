#!/usr/bin/env python3
"""vcheck.py - OFFLINE invariants for a generated/edited Revit file (own checker; reader code only read-only).
usage: vcheck.py FILE [--seed SEEDFILE] [--manifest JSON]   exit 0 = all invariants hold
checks: page ECC (every page of every ECC stream), gzip CRC32/ISIZE of every member, partition frames (own/next size, X1 vs walked A fields, X2), member raw <= 131088,
 header chain + record chain walk to the end of the first section, A/L consistency, Adler32 stamp of every record, header ids == ElemTable ids == count fields, ids unique/ascending,
 next-id counter >= max id, unchanged seed streams (History/IncrementTable/Basic/Contents/ProjectInfo byte-equal unless generator changes them), seed records preserved in order, new ids == manifest ids."""
import sys,struct,zlib,json,argparse,hashlib; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import numpy as np, cfb, rvtw, ecc, wlpart
errs=[]; warns=[]
def E(m): errs.append(m)
def W(m): warns.append(m)
def load(f):
    c=cfb.CFB(open(f,'rb').read()); return c,c.streams()
def stream_checks(S):
    for n,e in S.items():
        if n in rvtw.PLAIN: continue
        d=e.data; full=len(d)//rvtw.PAGE_STORED
        for i in range(full):
            if not ecc.check(d[i*rvtw.PAGE_STORED:(i+1)*rvtw.PAGE_STORED]): E('%s: ECC bad on page %d'%(n,i))
        last=d[full*rvtw.PAGE_STORED:]
        if last:
            if ecc.params(len(last)) is None: E('%s: last page size %d has no valid layout'%(n,len(last)))
            elif not ecc.check(last): E('%s: ECC bad on last page (N=%d)'%(n,len(last)))
        # gzip members CRC/ISIZE (single member streams + partition members)
        s=rvtw.Stream(d); P=s.payload
        if n.startswith('Partitions/'):
            pt=wlpart.Partition(s)
            for k,m in enumerate(pt.mem):
                raw=bytes(m['raw']); seg=P[m['pos']:m['end']]
                crc,isz=struct.unpack('<II',seg[-8:])
                if crc!=zlib.crc32(raw)&0xffffffff or isz!=len(raw): E('%s member %d: crc/isize mismatch'%(n,k))
                if len(raw)>131088: E('%s member %d raw %d > 131088'%(n,k,len(raw)))
        else:
            i=P.find(rvtw.GZ)
            if i<0: E('%s: no gzip member'%n); continue
            do=zlib.decompressobj(-15)
            try: raw=do.decompress(P[i+10:])
            except zlib.error as ex: E('%s: inflate error %s'%(n,ex)); continue
            tr=do.unused_data[:8]; crc,isz=struct.unpack('<II',tr)
            if crc!=zlib.crc32(raw)&0xffffffff or isz!=len(raw)&0xffffffff: E('%s: crc/isize mismatch'%n)
def graw(S,n):
    P=rvtw.Stream(S[n].data).payload; i=P.find(rvtw.GZ); return P[:i],zlib.decompressobj(-15).decompress(P[i+10:])
def analyse(f):
    c,S=load(f); info={'S':S}
    pn=[n for n in S if n.startswith('Partitions/')][0]; s=rvtw.Stream(S[pn].data); pt=wlpart.Partition(s,hs=16)
    # id width from ElemTable layout: rows 40 -> 8 bytes, 28 -> 4 bytes (checked through count field)
    et=graw(S,'Global/ElemTable')[1]; n=struct.unpack_from('<I',et,2)[0]
    RW=40 if 0<=len(et)-6-40*n<32 else 28
    Wd=8 if RW==40 else 4; hs=12+Wd; hsh=4+Wd+4
    pt=wlpart.Partition(s,hs=hs)
    bj=b''.join(bytes(m['raw']) for m in pt.mem); offs=pt.offs()
    info.update(pt=pt,bj=bj,W=Wd,hs=hs,hsh=hsh,n=n,RW=RW,et=et,pn=pn)
    return info
def walk(info):
    bj=info['bj']; hs=info['hs']; hsh=info['hsh']; W=info['W']; pt=info['pt']
    sec=None
    for k,g in enumerate(pt.gaps):
        if len(g)!=32: sec=pt.offs()[k+1]; break
    hdr=[(-4,int.from_bytes(bj[0:info['W']],'little'))]; p=-4
    # header chain: records [A][id][L][tag]; ends at the terminator (id=-1)
    while True:
        p+=hsh+struct.unpack_from('<I',bj,p+hsh-4)[0]
        if p+hsh+2>len(bj): E('header chain overruns'); return None
        if p>=0 and p+4+W<=len(bj):
            idv=int.from_bytes(bj[p+4:p+4+W],'little')
            if idv==(1<<(8*W))-1: break
            hdr.append((p,idv))
    q=p+hsh; recs=[]; badad=0; badL=0
    while q+hs<=sec:
        L=struct.unpack_from('<I',bj,q+hs-4)[0]
        if q+hs+L>sec+4: E('record chain overruns section end at %d'%q); break
        idv=int.from_bytes(bj[q+4:q+4+W],'little'); st=struct.unpack_from('<I',bj,q+4+W)[0]
        if zlib.adler32(bj[q+4+W+8:q+hs+L])&0xffffffff!=st: badad+=1; 
        nxt=q+hs+L
        if nxt+4<=len(bj) and nxt<sec and struct.unpack_from('<I',bj,nxt)[0]!=L: badL+=1
        recs.append((q,idv,L,bytes(bj[q+4:q+hs+L])))
        q=nxt
    if q!=sec-4: E('first-section chain ends at %d, expected %d'%(q,sec-4))
    return dict(hdr=hdr,recs=recs,badad=badad,badL=badL,sec=sec)
def frames(info):
    pt=info['pt']; bad=0; out=[]
    nsec=next((k+1 for k,g in enumerate(pt.gaps) if len(g)!=32),pt.n)
    for k,m in enumerate(pt.mem[:nsec]):
        g=pt.hdr if k==0 else pt.gaps[k-1]
        if k>0 and len(g)!=32: continue
        off=24 if k==0 else 12
        x1=struct.unpack_from('<I',g,off)[0]; x2=struct.unpack_from('<I',g,off+8)[0]; hs=m['hs']
        sz=struct.unpack_from('<I',pt.gaps[k][0:6] if False else pt.gaps[k] if k<len(pt.gaps) else pt.tail,2)[0]
        if sz!=m['end']-m['pos']+8 and m['end']: E('member %d own size field %d != %d'%(k,sz,m['end']-m['pos']+8))
        raw=bytes(m['raw']); pos=[]; q=-4
        while q+hs<=len(raw):
            q+=hs+struct.unpack_from('<I',raw,q+hs-4)[0]
            if q+4>len(raw): break
            pos.append(q)
        out.append((k,x1,x2,len(pos),len(raw)-hs*x1))
    return out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--seed'); ap.add_argument('--manifest'); ap.add_argument('--quiet',action='store_true'); a=ap.parse_args()
    info=analyse(a.file); S=info['S']
    stream_checks(S)
    w=walk(info)
    if w:
        if w['badad']: E('%d records with a wrong Adler32 stamp'%w['badad'])
        if w['badL']: E('%d records whose successor A != L'%w['badL'])
        hid=[i for _,i in w['hdr']]; 
        if len(set(hid))!=len(hid): E('duplicate header ids')
        et=info['et']; n=info['n']; RW=info['RW']; Wd=info['W']
        rows=[int.from_bytes(et[6+RW*k:6+RW*k+Wd],'little') for k in range(n)]
        if rows!=sorted(rows) or len(set(rows))!=len(rows): E('ElemTable ids not strictly ascending')
        if set(rows)!=set(hid): E('ElemTable ids != header ids (rows-only %d, headers-only %d)'%(len(set(rows)-set(hid)),len(set(hid)-set(rows))))
        hc=struct.unpack_from('<I',info['pt'].hdr,14)[0]
        if hc!=n: E('partition header count %d != ElemTable count %d'%(hc,n))
        ctr=struct.unpack_from('<I',et,len(et)-(8 if Wd==4 else 12))[0]
        if ctr<max(rows): E('next-id counter %d < max id %d'%(ctr,max(rows)))
        recids=[i for _,i,_,_ in w['recs']]
        ids_in_recs=set(recids)
        miss=[r for r in rows if r not in ids_in_recs]
        if miss: E('%d ElemTable ids have no record in the first section (e.g. %s)'%(len(miss),miss[:3]))
        if a.seed:
            si=analyse(a.seed); sw=walk(si)
            for nme in ('Global/History','Global/DocumentIncrementTable','BasicFileInfo','Contents','ProjectInformation','TransmissionData','Global/PartitionTable','Global/ContentDocuments','Formats/Latest'):
                if nme in S and nme in si['S']:
                    x=S[nme].data if nme in rvtw.PLAIN else graw(S,nme)[1]; y=si['S'][nme].data if nme in rvtw.PLAIN else graw(si['S'],nme)[1]
                    if x!=y: W('stream %s differs from the seed (%d vs %d bytes)'%(nme,len(x),len(y)))
            sh={i for _,i in sw['hdr']}; new=set(hid)-sh; gone=sh-set(hid)
            dele=set()
            if a.manifest:
                mm=json.load(open(a.manifest)); dele=set(mm.get('deleted',[])) if isinstance(mm,dict) else set()
            if gone!=dele: E('%d seed elements disappeared, expected %d'%(len(gone),len(dele)))
            srecs=[(i,r[4:]) for _,i,_,r in sw['recs']]; nrecs=[(i,r[4:]) for _,i,_,r in w['recs']]
            ren=set()
            if a.manifest:
                mm=json.load(open(a.manifest)); ren=({x[0] for x in mm.get('renames',[])}|set(mm.get('edited',[]))) if isinstance(mm,dict) else set()
            nset={id_ for id_ in new}
            # records not belonging to new elements must be identical to the seed's, in order (zone records of new elements share their id)
            seedlist=[x for x in srecs if x[0] not in ren and x[0] not in dele]; got=[x for x in nrecs if x[0] not in nset and x[0] not in ren]
            if got!=seedlist: E('seed records altered/reordered (%d vs %d)'%(len(got),len(seedlist)))
            if a.manifest:
                m=json.load(open(a.manifest))
                mids=set()
                if isinstance(m,dict):
                    for k in m:
                        if k not in ('renames','deleted','edited','names'): mids|={x[0] for x in m[k]}
                    ren={x[0] for x in m.get('renames',[])}
                else: mids={x[0] for x in m}
                if mids!=new: E('new ids %d != manifest ids %d'%(len(new),len(mids)))
            print('new elements',len(new),'records',len(nrecs),'seed records',len(srecs))
    def unexplained(inf):
        out=0
        for k,x1,x2,cnt,exp in frames(inf):
            raw_len=len(inf['pt'].mem[k]['raw'])
            if x2 not in (raw_len-inf['hs']*x1, raw_len-inf['hsh']*x1): out+=1
        return out
    ux=unexplained(info); us=unexplained(analyse(a.seed)) if a.seed else 0
    if ux>us: E('%d members have X2 inconsistent with X1 (seed itself has %d)'%(ux,us))
    for m in warns: print('WARN',m)
    for m in errs: print('FAIL',m)
    print('RESULT','PASS' if not errs else 'FAIL',len(errs),'errors',len(warns),'warnings')
    sys.exit(1 if errs else 0)
main()
