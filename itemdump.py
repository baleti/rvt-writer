import sys,os,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen
g=rvtgen.Gen(sys.argv[1])
for tid in map(int,sys.argv[2:]):
    t=g.template(tid); it=t['item']; print('==',tid,t['cls'],len(it))
    for o in range(0,len(it)-7):
        x=struct.unpack_from('<d',it,o)[0]
        if x!=0 and 1e-3<abs(x)<1e5 and abs(x*1000-round(x*1000))<1e-6*1000 or (x!=0 and 1e-4<abs(x)<1e5 and x==x and len(repr(x))<14): print(o,x)
    hl={n:(a,b) for n,a,b,_ in t['hlog']}; a,b=hl['Outline.m_minmax']; print('hdr outline',struct.unpack_from('<6d',t['hdr'],a))
