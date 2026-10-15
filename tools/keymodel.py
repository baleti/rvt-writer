#!/usr/bin/env python3
"""loose-octree key model for the wall item spatial key (item[316:320]); see HANDOFF-c5-writer.md"""
import math,struct,sys,os
def rnd(v): return math.floor(v+0.5-1e-9)
def axis(lo,hi,eps=0.0,strict=False,maxlev=6):
    for l in range(maxlev):
        s=4.0**(l+1); c=rnd((lo+hi)/2/s) if True else 0
        a,b=s*(c-1),s*(c+1)
        ok=(lo-eps>a and hi+eps<b) if strict else (lo-eps>=a-1e-9 and hi+eps<=b+1e-9)
        if ok: return c,l
    return None
def key(bb,eps=0.0,strict=False):
    x=axis(bb[0],bb[3],eps,strict); y=axis(bb[1],bb[4],eps,strict); z=axis(bb[2],bb[5],eps,strict)
    return x,y,z
def decode(tok):
    b0,b1,b2,b3=tok&255,(tok>>8)&255,(tok>>16)&255,tok>>24
    xf=((b1&15)<<8|b0); x=(xf>>4,xf&15); yn=b1>>4; y=(b2,yn&7,yn>>3); z=(b3>>3,b3&7)
    return x,y,z
if __name__=='__main__':
    sys.path.insert(0,os.path.expanduser("~/rvt-research/write-lab")); import rvtgen
    def rows(G,ids):
        for wid in ids:
            t=G.template(wid); hl={x[0]:x for x in t['hlog']}; a=hl['Outline.m_minmax'][1]
            yield wid,struct.unpack_from('<6d',t['hdr'],a),struct.unpack_from('<I',t['item'],316)[0]
    K=rvtgen.Gen('files/kwalls60.rte'); ids=[int(l.split()[1]) for l in open('files/kwalls60.txt') if l.startswith('W')]
    bad=0;n=0
    for wid,bb,tok in rows(K,ids):
        (xc,xl),(yc,yl,ysg),(zc,zl)=decode(tok); (px,py,pz)=key(bb)
        n+=1
        # sign: y cell magnitude with sign flag
        pyc=abs(py[0]) if py else None
        if not(px and py and pz) or (px[0]%4096,px[1])!=(xc,xl) or (pyc,py[1])!=(yc,yl) or (pz[0],pz[1])!=(zc,zl):
            bad+=1; print('MISMATCH',wid,['%.2f'%v for v in bb],'%08x'%tok,'tok',(xc,xl),(yc,yl,ysg),(zc,zl),'pred',px,py,pz)
    print('kwalls',n,'bad',bad)
