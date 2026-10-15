"""Partition-level rebuild with size-changing edits (member re-deflate, frame updates, page ECC)."""
import sys, struct, zlib, os
sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import numpy as np, rvtw, cfb
class Partition:
    """payload = hdr(44) + sum( member_k + gap_k ), gap_k = frame (32 bytes, [2:6]=own comp+8, [16:20]=next comp+8, [20:24]=X2 of next) [+ section end data]"""
    def __init__(self, stream_obj, hs=16):
        self.hs=hs
        self.st=stream_obj; P=stream_obj.payload
        st0=P.find(rvtw.GZ); self.hdr=bytearray(P[:st0]); self.hdr_len=st0
        pos=st0; self.mem=[]; self.gaps=[]
        while True:
            i=P.find(rvtw.GZ,pos)
            if i<0: break
            do=zlib.decompressobj(-15)
            try: raw=do.decompress(P[i+10:]); ok=do.eof
            except zlib.error: ok=False
            if not ok: pos=i+4; continue
            end=len(P)-len(do.unused_data)+8
            if self.mem: self.gaps.append(bytearray(P[self.mem[-1]['end']:i]))
            self.mem.append(dict(gzhdr=bytes(P[i:i+10]),raw=bytearray(raw),pos=i,end=end,dirty=False,delta=0))
            pos=end
        self.tail=bytes(P[self.mem[-1]['end']:])
        for k,m in enumerate(self.mem):
            g=self.gaps[k-1] if k else self.hdr
            off=12 if k else 24
            if k>0 and len(self.gaps[k-1])<32: m['hs']=self.hs; continue
            x1=struct.unpack_from('<I',g,off)[0]; x2=struct.unpack_from('<I',g,off+8)[0]
            m['hs']=round((len(m['raw'])-x2)/x1) if x1 else self.hs
        # regions: members before the first record-region member (hs == self.hs) are the ElementHeader region (hs = self.hs-4), everything after is the record region
        firstrec=next((k for k,m in enumerate(self.mem) if m['hs']==self.hs),0)
        for k,m in enumerate(self.mem): m['hs']=self.hs-4 if k<firstrec else self.hs
        self.n=len(self.mem)
    def offs(self):
        o=[0]
        for m in self.mem: o.append(o[-1]+len(m['raw']))
        return o
    def locate(self,off):
        o=self.offs(); k=int(np.searchsorted(o,off,side='right'))-1; return k,off-o[k]
    def replace(self, off, oldlen, new):
        k,a=self.locate(off); m=self.mem[k]
        assert a+oldlen<=len(m['raw']), 'edit straddles members'
        m['raw'][a:a+oldlen]=new; m['dirty']=True; m['delta']+=len(new)-oldlen
        return k
    LIMIT=131071   # Revit's own members reach 131088 in places; larger ones are left alone
    def rechunk_header_region(self,hsh=16):
        """members 0..h-1 (hs==16, contiguous from 0): re-split their bytes so that every member <= LIMIT, cutting at record starts; recompute X1"""
        h=0
        while h<self.n and self.mem[h]['hs']==hsh and (h==0 or len(self.gaps[h-1])==32): h+=1
        if not any(len(self.mem[k]['raw'])>self.LIMIT for k in range(h)): return
        buf=b''.join(bytes(self.mem[k]['raw']) for k in range(h))
        starts=[]; p=-4
        while p+hsh<=len(buf):
            p+=hsh+struct.unpack_from('<I',buf,p+hsh-4)[0]
            if p<len(buf): starts.append(p)          # position of the A of the next record (counted for X1)
            else: break
        # starts: positions of A fields (records 2..n and the first record of the next region)
        cuts=[0]; 
        import bisect
        while len(buf)-cuts[-1]>self.LIMIT:
            lim=cuts[-1]+self.LIMIT
            c=starts[bisect.bisect_right(starts,lim-4)-1]+4     # Revit cuts right after the A field of a record
            cuts.append(c)
        cuts.append(len(buf))
        assert len(cuts)-1<=h, 'header region needs more members'
        # members beyond len(cuts)-1 within region become empty? keep: put all remaining into the last used member and leave others untouched is not possible
        assert len(cuts)-1==h, 'member count change not supported'
        for k in range(h):
            m=self.mem[k]; m['raw']=bytearray(buf[cuts[k]:cuts[k+1]]); m['dirty']=True
            m['x1set']=sum(1 for s in starts if cuts[k]<=s+0 and s<cuts[k+1] and not (s+4==cuts[k]))
    def cascade(self):
        """Re-split dirty members (insertions may overflow LIMIT): every member starts right after an A field; cut after the largest A that fits;
        overflow is prepended to the next member (same region: 32-byte gap, same hs). X1 of every touched member is recomputed from the record chain."""
        import bisect
        j=0
        while j<self.n:
            m=self.mem[j]
            if not m['dirty'] and not m.get('carry'): j+=1; continue
            hs=m['hs']; buf=bytes(m['raw'])
            if m.get('carry'): buf=m.pop('carry')+buf
            pos=[]; p=-4
            while p+hs<=len(buf)+0:
                p+=hs+struct.unpack_from('<I',buf,p+hs-4)[0]
                if p<0 or p+4>len(buf): break
                pos.append(p)
            if len(buf)>self.LIMIT and pos:
                if not (j+1<self.n and len(self.gaps[j])==32 and self.mem[j+1]['hs']==hs):
                    assert len(self.gaps[j])==32,'cannot add a member after a section end (member %d)'%j
                    self.add_member_after(j)
                cut=pos[bisect.bisect_right(pos,self.LIMIT-4)-1]+4
                self.mem[j+1]['carry']=buf[cut:]+self.mem[j+1].get('carry',b''); self.mem[j+1]['dirty']=True
                buf=buf[:cut]
            m['raw']=bytearray(buf); m['dirty']=True
            m['x1set']=sum(1 for q in pos if q+4<=len(buf))
            j+=1
    def insert_at(self,pos,data):
        """insert `data` (a complete chain: starts with a record id, ends with the A field of the record that follows) at joined offset `pos`,
        which must be right after an A field (or 0). The member is split at pos and the data becomes new members (<= LIMIT each, cut after an A)."""
        import bisect
        k,off=self.locate(pos); m=self.mem[k]; hs=m['hs']
        if off==0 and k>0: pass
        raw=bytes(m['raw']); left=raw[:off]; right=raw[off:]
        # cut data into chunks
        chunks=[]; buf=data
        while True:
            p=-4; ps=[]
            while p+hs<=len(buf):
                p+=hs+struct.unpack_from('<I',buf,p+hs-4)[0]
                if p+4>len(buf): break
                ps.append(p)
            assert ps and ps[-1]+4==len(buf) or len(buf)==0,'data must end with an A field'
            if len(buf)<=self.LIMIT: chunks.append(buf); break
            cut=ps[bisect.bisect_right(ps,self.LIMIT-4)-1]+4
            chunks.append(buf[:cut]); buf=buf[cut:]
        parts=([left] if left else [])+chunks+([right] if right else [])
        newm=[]
        for pr in parts:
            nm=dict(gzhdr=m['gzhdr'],raw=bytearray(pr),pos=0,end=0,dirty=True,delta=0,hs=hs); newm.append(nm)
        tailgap=self.gaps[k] if k<len(self.gaps) else None
        # gaps: inner boundaries get a copy of the frame that followed member k
        frames=[bytearray(tailgap) for _ in range(len(parts)-1)] if tailgap is not None else []
        self.mem[k:k+1]=newm
        self.gaps[k:k]=frames
        self.n=len(self.mem)
    def add_member_after(self,j):
        """new empty member after member j (same hs); its frame is a copy of the frame that followed j"""
        mj=self.mem[j]
        nm=dict(gzhdr=mj['gzhdr'],raw=bytearray(),pos=0,end=0,dirty=True,delta=0,hs=mj['hs'])
        self.mem.insert(j+1,nm); self.gaps.insert(j+1,bytearray(self.gaps[j])); self.n+=1
    def rebuild(self):
        self.cascade()
        P0=self.st.payload
        newmem=[]
        for k,m in enumerate(self.mem):
            if m['dirty']: newmem.append(rvtw.gz_member(bytes(m['raw']),m['gzhdr'],None))
            else: newmem.append(bytes(P0[m['pos']:m['end']]))
        fr=[bytearray(g) for g in self.gaps]+[bytearray(self.tail)]   # frame after member k is fr[k] (last: tail)
        hdr=bytearray(self.hdr)
        for k,m in enumerate(self.mem):
            if not m['dirty']: continue
            val=len(newmem[k])+8
            if os.environ.get('WL_NOFRAME'): continue
            struct.pack_into('<I',fr[k],2,val)                      # own size
            # 'next' fields live in the frame before member k when it is inside the same section (frame k-1 is a 32-byte frame preceding this member)
            if k>0:
                struct.pack_into('<I',fr[k-1],16,val)
                x1=m['x1set'] if 'x1set' in m else struct.unpack_from('<I',fr[k-1],12)[0]+m.get('dx1',0); struct.pack_into('<I',fr[k-1],12,x1)
                struct.pack_into('<I',fr[k-1],20,len(m['raw'])-m['hs']*x1)
            else:
                struct.pack_into('<I',hdr,28,val)
                x1=m['x1set'] if 'x1set' in m else struct.unpack_from('<I',hdr,24)[0]+m.get('dx1',0); struct.pack_into('<I',hdr,24,x1)
                struct.pack_into('<I',hdr,32,len(m['raw'])-m['hs']*x1)
        if getattr(self,'hdr_dn',0): struct.pack_into('<I',hdr,14,struct.unpack_from('<I',hdr,14)[0]+self.hdr_dn)
        out=bytearray(hdr)
        for k in range(self.n): out+=newmem[k]; out+=fr[k]
        return bytes(out)
