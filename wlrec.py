"""locate/decode single element records with field offsets (uses session-176 modules read-only)"""
import sys, struct
sys.path.insert(0,'/home/user1/rvt-research'); sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import numpy as np
import rvt_scan as S, rvt_decode as D, rvt2text as T, rvt_es as ES, rvt_inventory as I
import cfb, rvtw
class Model:
    def __init__(self, path):
        self.path=path
        self.o,self.cls,self.ids=S.load(path); self.IDW=S.id_size(self.cls); self.IDF='<I' if self.IDW==4 else '<Q'
        self.sch=D.Schema(self.cls); self.dec=D.Dec(self.sch,idsize=self.IDW); self.etags=I.element_tags(self.cls)
        try: self.dec.es_schemas=ES.load(path)[0]
        except Exception: self.dec.es_schemas={}
        self.c=cfb.CFB(open(path,'rb').read())
        self.parts={}
        for sn,e in self.c.streams().items():
            if sn.startswith('Partitions/'):
                st=rvtw.Stream(e.data); P=st.payload; st0=P.find(rvtw.GZ)
                mem=rvtw.members(P,st0)
                raws=[rvtw.read_member(P,pos)[0] for pos,end,_ in mem]
                self.parts[sn]=dict(stream=st,mem=mem,raws=raws,joined=b''.join(raws),offs=np.cumsum([0]+[len(r) for r in raws]))
        self.idarr=np.array(sorted(self.ids),dtype=np.uint32 if self.IDW==4 else np.uint64)
    def find(self, eid):
        """yield (part, offset, record, trace) for every decodable record of element eid"""
        for pn,p in self.parts.items():
            b=p['joined']
            for i in S.header_candidates(b,np.array([eid],dtype=self.idarr.dtype),self.IDW):
                for short in (False,True):
                    tag=struct.unpack_from('<H',b,i+12+self.IDW-(4 if short else 0))[0]
                    if tag not in self.etags: continue
                    self.dec.log=[]; self.dec.trace=True
                    try: r,q=self.dec.record(b,i,short)
                    except Exception: continue
                    if r['fields'].get('m_id')!=eid: continue
                    yield pn,i,r,list(self.dec.log),q
