"""rvtgen: add many generated elements (clones of template records) to a Revit-written .rte/.rvt using my own writer (see LOG.md M9-M11).
Seed = a Revit-saved file that already contains ONE element of the wanted kind (its header/record/dummy-item records are the templates)."""
import sys,struct,os,zlib; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
os.environ.setdefault('RVT_GEOM','1')
import wledit,wlrec,rvtw,cfb,wlpart
def _spans(pt,base,old,new):
    """apply old->new at partition offset base as the minimal changed spans (back to front), so a record that straddles two gzip
    members is edited inside each member without moving bytes across the boundary"""
    import difflib
    for tag,a0,a1,b0,b1 in reversed(difflib.SequenceMatcher(None,old,new,autojunk=False).get_opcodes()):
        if tag!='equal': pt.replace(base+a0,a1-a0,new[b0:b1])
class Gen:
    def __init__(self, seed):
        self.e=wledit.Editor(seed); e=self.e; self.W=e.m.IDW; W=self.W
        self.pn=list(e.m.parts)[0]; self.pt=e.part(self.pn); self.bj=e.m.parts[self.pn]['joined']
        self.hs=12+W; self.hsh=4+W+4; self.IDF='<I' if W==4 else '<Q'; self.RW=28 if W==4 else 40; self.CTR=8 if W==4 else 12
        self.EHT=struct.pack('<H',e.m.sch.by['ElementHeader']+12)
        er=self._et(); self.counter=struct.unpack_from('<I',er,len(er)-self.CTR)[0]; self.nextid=self.counter+1
        self.new=[]      # (hdr_noA, rec_withA, item_noA, id)
        self.rows=[]; self.maxid=max(e.m.ids)
    def _et(self):
        P=rvtw.Stream(self.e.m.c.streams()['Global/ElemTable'].data).payload; i=P.find(rvtw.GZ); return zlib.decompressobj(-15).decompress(P[i+10:])
    def _etrows(self):
        """ElemTable rows by element id (first row per id), cached per ElemTable stream object"""
        d=self.e.m.c.streams()['Global/ElemTable'].data
        if getattr(self,'_etkey',None) is not d:
            et=self._et(); n=struct.unpack_from('<I',et,2)[0]; RW=self.RW; W=self.W; m={}
            for k in range(n):
                r=bytes(et[6+RW*k:6+RW*k+RW]); m.setdefault(int.from_bytes(r[:W],'little'),r)
            self._etkey=d; self._etmap=m
        return self._etmap
    def _hdr_at(self, idb):
        """offset of the element header of id bytes idb: first occurrence followed (after the length) by the ElementHeader tag"""
        bj=self.bj; W=self.W; k=-1; lim=len(bj)-20
        while True:
            k=bj.find(idb,k+1)
            if k<0 or k>=lim: raise IndexError('no element header')
            if bj[k+W+4:k+W+6]==self.EHT: return k
    def template(self, tid):
        """returns dict with header/record/item bytes of existing element tid and the field offsets needed to patch them"""
        e=self.e; W=self.W; bj=self.bj; idb=struct.pack(self.IDF,tid); hs_=self.hs
        pn,i,r,log,q=e.trace(tid); rec=bytes(bj[i:q])
        hk=self._hdr_at(idb)
        Lh=struct.unpack_from('<I',bj,hk+W)[0]; hdr=bytes(bj[hk:hk+W+4+Lh])
        # zone record: a record (A,id,stamp,L,tag) with this id, valid chain (next A == L), not the element record itself nor its header
        cand=[]; k=-1
        while True:
            k=bj.find(idb,k+1)
            if k<0: break
            if k==i+4 or k<4: continue
            if bj[k+W+4:k+W+6]==self.EHT[:0] : pass
            if k+W+10>len(bj): continue
            L=struct.unpack_from('<I',bj,k+W+4)[0]; tag=struct.unpack_from('<H',bj,k+W+8)[0]
            if not (12<=tag<12+len(e.m.cls)) or tag==struct.unpack('<H',self.EHT)[0] or L>1000000 or k-4+hs_+L+4>len(bj): continue
            if struct.unpack_from('<I',bj,k-4+hs_+L)[0]!=L: continue
            if struct.unpack_from('<I',bj,k)[0] if False else False: pass
            cand.append(k)
        zk=[c for c in cand if c>i+len(rec)][0] if [c for c in cand if c>i+len(rec)] else cand[-1]
        zL=struct.unpack_from('<I',bj,zk+W+4)[0]; item=bytes(bj[zk:zk+W+4+4+zL]); self.itag=item[W+8:W+10]   # id..tag..body (no A)
        # row
        row=self._etrows()[tid]
        e.m.dec.log=[]; e.m.dec.trace=True
        e.m.dec.record(bj,hk-4,True); hlog=[(l[1],l[2]-hk,l[3]-hk,l[4]) for l in e.m.dec.log]
        return dict(tid=tid,rec=rec,hdr=hdr,item=item,row=row,hlog=hlog,log=[(l[1],l[2]-i,l[3]-i,l[4]) for l in log],cls=r['class'])
    def locate(self, tid):
        e=self.e; W=self.W; bj=self.bj; idb=struct.pack(self.IDF,tid); hs_=self.hs
        pn,i,r,log,q=e.trace(tid)
        hk=self._hdr_at(idb)
        hlen=W+4+struct.unpack_from('<I',bj,hk+W)[0]
        zs=[]; k=-1
        while True:
            k=bj.find(idb,k+1)
            if k<0: break
            if k==i+4 or k<4: continue
            L=struct.unpack_from('<I',bj,k+W+4)[0]; tag=struct.unpack_from('<H',bj,k+W+8)[0]
            if not (12<=tag<12+len(e.m.cls)) or tag==struct.unpack('<H',self.EHT)[0] or L>1000000 or k-4+hs_+L+4>len(bj): continue
            if struct.unpack_from('<I',bj,k-4+hs_+L)[0]!=L: continue
            if k>q: zs.append((k-4,hs_+L))
        return dict(hdr=(hk,hlen),rec=(i,q-i),zone=zs)
    def delete(self, tid):
        """remove element tid completely: header, record, zone records, ElemTable row (+count, counter untouched), partition header count"""
        L=self.locate(tid); pt=self.pt; bj=self.bj; ops=[]
        for (st,ln) in L['zone']+[L['rec']]:
            A=bytes(bj[st:st+4]); ops.append((st,lambda st=st,ln=ln,A=A: pt.replace(st,ln+4,A)))
        hk,hl=L['hdr']
        if hk==0: ops.append((0,lambda: pt.replace(0,hl+4,b'')))
        else: ops.append((hk-4,lambda: pt.replace(hk-4,hl+8,bytes(bj[hk-4:hk]))))
        self.edits=getattr(self,'edits',[])+ops; self.deleted=getattr(self,'deleted',[])+[tid]
    def add_deletion_children(self, tid, new_ids):
        """append new_ids (e.g. hosted instances) to element tid's header deletion list (ElementParents.m_deletion) - the host then regenerates when a child changes"""
        W=self.W; bj=self.bj; T=self.template(tid); hl={n:(o,e) for n,o,e,_ in T['hlog']}; d0,d1=hl['ElementParents.m_deletion']
        L=self.locate(tid); hk,hlen=L['hdr']; old=bytes(bj[hk:hk+hlen]); assert old==T['hdr']
        new=bytearray(old[:d0]); cnt=struct.unpack_from('<I',old,d0)[0]; new+=struct.pack('<I',cnt+len(new_ids))+old[d0+4:d1]+b''.join(struct.pack(self.IDF,i) for i in new_ids)+old[d1:]
        struct.pack_into('<I',new,W,len(new)-W-4); pt=self.pt
        self.edits=getattr(self,'edits',[])+[(hk,lambda: pt.replace(hk,hlen+4,bytes(new)+struct.pack('<I',len(new)-W-4)))]
    def replace_existing(self, tid, hdr=None, rec=None):
        """replace the header and/or element record of an EXISTING element (sizes may change). hdr = [id][Lh].. as template()['hdr'];
        rec = full record as template()['rec'] (A,id,stamp,L,..; restamped here); the next header/record's A link is rewritten"""
        W=self.W; pt=self.pt; L=self.locate(tid); ops=[]
        if rec is not None:
            i,ln=L['rec']; r=self.stamp(bytes(rec)); old=bytes(self.bj[i:i+ln])
            def f(i=i,ln=ln,r=r,old=old):
                pt.replace(i+ln,4,struct.pack('<I',len(r)-self.hs))      # next record's A (may sit in the next member)
                _spans(pt,i,old,r)
            ops.append((i+ln+0.5,f))      # keyed past the record end: runs before inserts at i or i+4 (441 is the first record of the region)
        if hdr is not None:
            hk,hlen=L['hdr']; h=bytearray(hdr); struct.pack_into('<I',h,W,len(h)-W-4)
            oh=bytes(self.bj[hk:hk+hlen])
            def fh(hk=hk,hlen=hlen,h=bytes(h),oh=oh): pt.replace(hk+hlen,4,struct.pack('<I',len(h)-W-4)); _spans(pt,hk,oh,h)
            ops.append((hk+0.5,fh))
        self.edits=getattr(self,'edits',[])+ops
    def add(self, hdr, rec, item):
        """hdr/item/rec already patched for the new id (id taken from rec header)"""
        W=self.W; nid=self.nextid; self.nextid+=1; return nid
    def stamp(self,rec):
        W=self.W; hs=self.hs; r=bytearray(rec)
        struct.pack_into('<I',r,4+W+4,len(r)-hs); struct.pack_into('<I',r,4+W,zlib.adler32(bytes(r[4+W+8:]))&0xffffffff); return bytes(r)
    def _finish_delete(self):
        e=self.e; dl=set(self.deleted); W=self.W; RW=self.RW; pt=self.pt
        def fn(raw):
            n=struct.unpack_from('<I',raw,2)[0]; rows=raw[6:]; keep=[rows[k*RW:(k+1)*RW] for k in range(n) if int.from_bytes(rows[k*RW:k*RW+W],'little') not in dl]
            out=bytearray(raw[:6]); struct.pack_into('<I',out,2,len(keep)); out+=b''.join(keep)+rows[n*RW:]; return bytes(out)
        e.global_edit('Global/ElemTable',fn); pt.hdr_dn=-len(dl)
        fs=[f for _,f in getattr(self,'latest_edits',[])]
        if fs:
            def comp(raw):
                for f in fs: raw=f(raw)
                return raw
            e.global_edit('Global/Latest',comp)
    def commit(self, dst, templ_row=None):
        e=self.e; pt=self.pt; W=self.W; bj=self.bj; hs=self.hs
        n=len(self.new)
        if n==0:
            for off,fn in sorted(list(getattr(self,'edits',[])),key=lambda x:-x[0]): fn()
            if getattr(self,'deleted',None): self._finish_delete()
            e.save(dst); return
        p=-4
        while True:
            p+=self.hsh+struct.unpack_from('<I',bj,p+self.hsh-4)[0]
            if bj[p+self.hsh:p+self.hsh+2]!=self.EHT: break
        if struct.unpack_from('<I',bj,p+self.hsh-4)[0]==0 and bj[p+4:p+4+W]==b'\xff'*W: p+=self.hsh      # terminator record (id -1, L 0)
        q_rec=p          # A of the first element record: the ElementHeader chain ends here
        _o=pt.offs()
        for _k,_m in enumerate(pt.mem): _m['hs']=self.hsh if _o[_k+1]<=q_rec+4 else self.hs
        _pat=bytes.fromhex('02000000')+struct.pack('<H',e.m.sch.by['SerializedDummy']+12); _ids=set(e.m.ids); _j=-1; sit0=None
        while True:      # first serialized dummy item (same rule as a full scan, via bytes.find)
            _j=bj.find(_pat,_j+1)
            if _j<0: break
            k=_j-(W+4)
            if 8<=k<len(bj)-22 and struct.unpack_from(self.IDF,bj,k)[0] in _ids: sit0=k; break
        if sit0 is None: raise ValueError('no serialized dummy item')
        q_item=sit0-4
        # chains
        items=b''.join(it+struct.pack('<I',struct.unpack_from('<I',it,W+4)[0]) for (_,_,it,_) in self.new)
        recs=b''; prevL=None
        for k,(_,rec,_,_) in enumerate(self.new):
            L=len(rec)-hs
            recs+=(rec[4:] if k==0 else struct.pack('<I',prevL)+rec[4:]); prevL=L
        recs+=struct.pack('<I',prevL)
        hdrs=b''
        for (h,_,_,_) in self.new:
            Lh=struct.unpack_from('<I',h,W)[0]; hdrs+=h+struct.pack('<I',Lh)
        # descending offsets: item zone, records, headers
        assert q_item>q_rec
        ins=q_rec+4
        for _ in range(int(os.environ.get('REC_SKIP','0'))):          # experiment: Revit saves recently touched elements first (GCSTracker, then new ones)
            ins=ins-4+hs+struct.unpack_from('<I',bj,ins-4+4+W+4)[0]+4
        ops=[(q_item+4,lambda: pt.insert_at(q_item+4,items)),(ins,lambda: pt.insert_at(ins,recs)),(0,lambda: pt.insert_at(0,hdrs))]+list(getattr(self,'edits',[]))
        for off,fn in sorted(ops,key=lambda x:-x[0]): fn()
        pt.hdr_dn=n-len(getattr(self,'deleted',[]) or [])
        # ElemTable
        rows=self.rows
        def fn(raw):
            cnt=struct.unpack_from('<I',raw,2)[0]; body=raw[6:]
            out=bytearray(raw[:6]); struct.pack_into('<I',out,2,cnt+len(rows)); out+=body[:cnt*self.RW]+b''.join(rows)+body[cnt*self.RW:]
            struct.pack_into('<I',out,len(out)-self.CTR,self.nextid-1); return bytes(out)
        if not getattr(self,'skip_elemtable',False): e.global_edit('Global/ElemTable',fn)
        fs=[f for _,f in getattr(self,'latest_edits',[])]
        if fs:
            def comp(raw):
                for f in fs: raw=f(raw)
                return raw
            e.global_edit('Global/Latest',comp)
        e.save(dst)
