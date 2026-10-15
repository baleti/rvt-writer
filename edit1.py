import sys, struct, zlib
sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtw, cfb
def edit_same_size(src, dst, stream, repls, part_hdr=44):
    """repls: list of (old_utf16_text, new_utf16_text) same char count. Returns report."""
    c=cfb.CFB(open(src,'rb').read())
    rep=[]
    for sn,e in c.streams().items():
      if not (sn==stream or (stream=='*' and sn.startswith('Partitions/'))): continue
      s=rvtw.Stream(e.data); P=bytearray(s.payload)
      st0=P.find(rvtw.GZ); mem=rvtw.members(bytes(P),st0)
      rep+=_do(P,mem,repls)
      e.data=s.build(bytes(P),keep_spare=True)
    assert rep,'nothing replaced'
    cfb.write(c,dst)
    return rep
def _do(P,mem,repls):
    rep=[]
    for old,new in repls:
        assert len(old)==len(new)
        ob=old.encode('utf-16le'); nb=new.encode('utf-16le')
        for (pos,end,rawlen) in mem:
            raw,_=rvtw.read_member(bytes(P),pos)
            n=raw.count(ob)
            if not n: continue
            raw2=raw.replace(ob,nb)
            hdr=bytes(P[pos:pos+10]); target=(end-8)-(pos+10)
            m2=rvtw.gz_member(raw2,hdr,target)
            assert len(m2)==end-pos
            P[pos:end]=m2; rep.append((old,new,pos,n))
    return rep
def diff_bytes(a,b):
    A=open(a,'rb').read(); B=open(b,'rb').read()
    ca=cfb.CFB(A); cb=cfb.CFB(B)
    out={}
    for k,e in ca.streams().items():
        f=cb.streams()[k]
        if e.data!=f.data:
            n=sum(1 for x,y in zip(e.data,f.data) if x!=y) if len(e.data)==len(f.data) else -1
            out[k]=(len(e.data),len(f.data),n)
    return out
if __name__=='__main__':
    src,dst,stream=sys.argv[1:4]
    repls=[tuple(a.split('=>')) for a in sys.argv[4:]]
    print(edit_same_size(src,dst,stream,repls)); print(diff_bytes(src,dst))
