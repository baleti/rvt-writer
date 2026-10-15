"""size-changing edits: string field of one element record (+ record length chain + member frames)"""
import sys, os, struct
os.environ.setdefault('EXACT','1'); os.environ.setdefault('KEEPREST','1')
sys.path.insert(0,'/home/user1/rvt-research/write-lab')
os.environ.setdefault('RVT_GEOM','1')
import wlrec, wlpart, rvtw, cfb
def _shrinkpad(payload,st):
    """a rebuilt stream payload that is SHORTER than the Revit-written one (our gzip packs tighter) would get fewer full pages and a new,
    computed last-page size, which Revit 2026 rejects for some sizes (CorruptModelException / CArchiveException 105: 2026-10-15 bisect, small
    additions to house_base). Zero-pad it to the original length so the page layout (full pages + Revit's own last page) stays Revit's."""
    if os.environ.get('SHRINKPAD','1')!='1': return payload
    cap=st.full*rvtw.PAGE_PAYLOAD+getattr(st,'cap_last',0)
    return payload+b'\0'*(cap-len(payload)) if len(payload)<cap else payload
class Editor:
    def __init__(self, path):
        self.m=wlrec.Model(path); self.parts={}; self.globals={}
    def part(self,pn):
        if pn not in self.parts: self.parts[pn]=wlpart.Partition(self.m.parts[pn]['stream'],hs=12+self.m.IDW)
        return self.parts[pn]
    def modify(self, eid, edits, which=0):
        """edits: list of (joined_offset, oldlen, newbytes) inside one record of eid; rewrites the record with fixed length fields,
        Adler32 stamp and the next record's A link"""
        import zlib
        pn,i,r,log,q=self.trace(eid,which); pt=self.part(pn); b=self.m.parts[pn]['joined']; W=self.m.IDW; hs=12+W
        rec=bytearray(b[i:q])
        for off,o,n in sorted(edits,key=lambda e:-e[0]): rec[off-i:off-i+o]=n
        if not r['short']:
            struct.pack_into('<I',rec,4+W+4,len(rec)-hs)
            struct.pack_into('<I',rec,4+W,zlib.adler32(bytes(rec[4+W+8:]))&0xffffffff)
        else:
            struct.pack_into('<I',rec,4+W,zlib.adler32(bytes(rec[4+W+4:]))&0xffffffff)
        pt.replace(q,4,struct.pack('<I',len(rec)-hs))       # next record's A (first: higher offset)
        k=pt.replace(i,q-i,bytes(rec))
        return dict(member=k,delta=len(rec)-(q-i),part=pn)
    def set_string(self, eid, fieldname, newtext, which=0, match=None):
        pn,i,r,log,q=self.trace(eid,which)
        ent=[l for l in log if l[1]==fieldname and (match is None or l[4]==match)][0]
        nb=(lambda b: struct.pack('<I',len(b)//2)+b)(newtext.encode('utf-16le'))
        return self.modify(eid,[(ent[2],ent[3]-ent[2],nb)],which)
    def delete(self, eid, which=0):
        pn,i,r,log,q=self.trace(eid,which); pt=self.part(pn); b=self.m.parts[pn]['joined']
        A=b[i:i+4]
        k=pt.replace(i,(q-i)+4,A)
        pt.mem[k]['dx1']=pt.mem[k].get('dx1',0)-1
        return dict(member=k,removed=q-i)
    def clone(self, src_eid, new_eid, field_edits=None, which=0):
        """insert a copy of element src_eid (new id) right after it. field_edits: list of (log_entry_name, occurrence, newbytes_fn(oldbytes)->newbytes)"""
        pn,i,r,log,q=self.trace(src_eid,which); pt=self.part(pn); b=self.m.parts[pn]['joined']; W=self.m.IDW; hs=12+W
        rec=bytearray(b[i:q]); base=i
        def rel(o): return o-base
        # new id in header and Element.m_id
        idb=new_eid.to_bytes(W,'little')
        rec[4:4+W]=idb
        for l in log:
            if l[1]=='Element.m_id': rec[rel(l[2]):rel(l[3])]=idb
        # field edits applied descending
        eds=[]
        for name,occ,fn in (field_edits or []):
            ent=[l for l in log if l[1]==name][occ]; eds.append((rel(ent[2]),rel(ent[3]),fn(bytes(rec[rel(ent[2]):rel(ent[3])]))))
        for a,z,nb in sorted(eds,key=lambda x:-x[0]): rec[a:z]=nb
        oldL=struct.unpack_from('<I',b,i+4+W+4)[0]
        struct.pack_into('<I',rec,0,oldL)                      # A = previous record (the original) length - hs
        struct.pack_into('<I',rec,4+W+4,len(rec)-hs)           # own length
        import zlib; struct.pack_into('<I',rec,4+W,zlib.adler32(bytes(rec[4+W+8:]))&0xffffffff)   # stamp-lo = Adler32 of the record body
        k=pt.replace(q,4,bytes(rec)+struct.pack('<I',len(rec)-hs))
        pt.mem[k]['dx1']=pt.mem[k].get('dx1',0)+1
        return dict(member=k,newlen=len(rec))
    def trace(self,eid,which=0):
        pn,i,r,log,q=list(self.m.find(eid))[which]; return pn,i,r,log,q
    def global_edit(self, name, fn):
        """fn(raw bytes)->new raw for a single-gzip-member Global/* stream"""
        c=self.m.c; s=rvtw.Stream(c.streams()[name].data); P=s.payload; st0=P.find(rvtw.GZ)
        raw,end=rvtw.read_member(P,st0); new=fn(raw)
        tgt=(end-8)-(st0+10)
        try: mem=rvtw.gz_member(new,P[st0:st0+10],tgt) if os.environ.get('EXACT') else rvtw.gz_member(new,P[st0:st0+10],None)
        except ValueError: mem=rvtw.gz_member(new,P[st0:st0+10],None)
        self.globals[name]=(s,P[:st0]+mem+(P[end:] if os.environ.get('KEEPREST') else b''))
    def save(self,dst):
        c=self.m.c
        for pn,pt in self.parts.items():
            payload=pt.rebuild()
            st_=self.m.parts[pn]['stream']
            payload=_shrinkpad(payload,st_)
            if os.environ.get('FULLPAD','1')=='1' and len(payload)>st_.full*rvtw.PAGE_PAYLOAD+getattr(st_,'cap_last',0):
                payload=payload+b'\0'*((-len(payload))%rvtw.PAGE_PAYLOAD)      # last page becomes a full page (N=65249): the one page size known to be valid
            r_=len(payload)%rvtw.PAGE_PAYLOAD; c.streams()[pn].data=st_.build(payload,N_last=(rvtw.min_last_page(r_) if os.environ.get('MINLAST') else None),keep_spare=False)
        for name,(s,payload) in self.globals.items():
            payload=_shrinkpad(payload,s)
            if os.environ.get('FULLPAD','1')=='1' and not os.environ.get('GMINLAST') and len(payload)>s.full*rvtw.PAGE_PAYLOAD+getattr(s,'cap_last',0):
                payload=payload+b'\0'*((-len(payload))%rvtw.PAGE_PAYLOAD)
            if os.environ.get('GMINLAST') and len(payload)>s.full*rvtw.PAGE_PAYLOAD+getattr(s,'cap_last',0):
                r_=len(payload)-(len(payload)//rvtw.PAGE_PAYLOAD)*rvtw.PAGE_PAYLOAD
                c.streams()[name].data=s.build(payload,N_last=rvtw.min_last_page(r_),keep_spare=False)
            else: c.streams()[name].data=s.build(payload,keep_spare=False)
        cfb.write(c,dst)
