import sys, struct, zlib
sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import numpy as np, rvtw, cfb
class Patcher:
    """same-size byte patches at offsets of the joined decoded buffer of a Partitions/* stream"""
    def __init__(self, model):
        self.m=model; self.edits={}   # part -> {off:bytes}
        self.log=[]
    def set(self, part, off, data, note=''):
        self.edits.setdefault(part,{})[off]=bytes(data); self.log.append((part,off,len(data),note))
    def save(self, dst):
        m=self.m; c=m.c; touched=0
        for pn,ed in self.edits.items():
            p=m.parts[pn]; raws=[bytearray(r) for r in p['raws']]; offs=p['offs']
            dirty=set()
            for off,data in ed.items():
                a=off; b=off+len(data)
                k=int(np.searchsorted(offs,a,side='right'))-1
                pos=0
                while pos<len(data):
                    base=int(offs[k]); lim=int(offs[k+1])
                    n=min(len(data)-pos, lim-(a+pos))
                    raws[k][a+pos-base:a+pos-base+n]=data[pos:pos+n]; dirty.add(k); pos+=n; k+=1
            P=bytearray(p['stream'].payload)
            for k in sorted(dirty):
                pos,end,_=p['mem'][k]
                hdr=bytes(P[pos:pos+10]); target=(end-8)-(pos+10)
                m2=rvtw.gz_member(bytes(raws[k]),hdr,target); assert len(m2)==end-pos
                P[pos:end]=m2
            c.streams()[pn].data=p['stream'].build(bytes(P),keep_spare=True); touched+=len(dirty)
        cfb.write(c,dst); return touched
