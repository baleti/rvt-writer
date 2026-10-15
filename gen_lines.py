#!/usr/bin/env python3
"""gen_lines.py - generate a Revit file full of model lines (Koch snowflake / Sierpinski / spiral / star) with my own .rvt writer.
seed: Revit-saved .rte that already holds one sketch plane + one model line (template records). Verification: Revit API dump (verify_lines.cs)."""
import sys,struct,math,argparse,json,os; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtgen,genlib
def koch(depth,size):
    pts=[(0,0),(size,0),(size/2,size*math.sqrt(3)/2)]
    pts=[(0,0),(size,0),(size/2,size*math.sqrt(3)/2),(0,0)][::-1]  # counter-clockwise
    for _ in range(depth):
        out=[]
        for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
            dx,dy=(x1-x0)/3,(y1-y0)/3
            a=(x0+dx,y0+dy); b=(x0+2*dx,y0+2*dy)
            c=(a[0]+dx*0.5-dy*math.sqrt(3)/2, a[1]+dy*0.5+dx*math.sqrt(3)/2)
            out+= [(x0,y0),a,c,b]
        out.append(pts[-1]); pts=out
    return [(pts[i],pts[i+1]) for i in range(len(pts)-1)]
def sierpinski(depth,size):
    def tri(a,b,c,d):
        if d==0: return [(a,b),(b,c),(c,a)]
        ab=((a[0]+b[0])/2,(a[1]+b[1])/2); bc=((b[0]+c[0])/2,(b[1]+c[1])/2); ca=((c[0]+a[0])/2,(c[1]+a[1])/2)
        return tri(a,ab,ca,d-1)+tri(ab,b,bc,d-1)+tri(ca,bc,c,d-1)
    return tri((0,0),(size,0),(size/2,size*math.sqrt(3)/2),depth)
def spiral(n,size):
    pts=[]; phi=(1+5**.5)/2
    for i in range(n+1):
        r=size*0.02*i**0.9; t=i*2*math.pi/phi/1.0*0.35
        pts.append((r*math.cos(t),r*math.sin(t)))
    return [(pts[i],pts[i+1]) for i in range(n)]
def star(n,size):
    return [((0,0),(size*math.cos(2*math.pi*i/n)*(0.5+0.5*math.sin(i*0.7)**2),size*math.sin(2*math.pi*i/n)*(0.5+0.5*math.sin(i*0.7)**2))) for i in range(n)]
SHAPES={'koch':lambda a:koch(a.depth,a.size),'sierpinski':lambda a:sierpinski(a.depth,a.size),'spiral':lambda a:spiral(a.n,a.size),'star':lambda a:star(a.n,a.size)}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--seed',default='files/k_line.rte'); ap.add_argument('--template',type=int,default=301554)
    ap.add_argument('--shape',default='koch',choices=SHAPES); ap.add_argument('--depth',type=int,default=2); ap.add_argument('--n',type=int,default=60)
    ap.add_argument('--size',type=float,default=100.0); ap.add_argument('--ox',type=float,default=0.0); ap.add_argument('--oy',type=float,default=0.0)
    ap.add_argument('--out',required=True); ap.add_argument('--manifest')
    a=ap.parse_args()
    segs=SHAPES[a.shape](a); segs=[((p[0]+a.ox,p[1]+a.oy),(q[0]+a.ox,q[1]+a.oy)) for p,q in segs]
    g=rvtgen.Gen(a.seed); T=g.template(a.template); W=g.W
    L={n:(o,z) for n,o,z,_ in T['log']}
    zt=struct.unpack_from('<3d',T['rec'],L['GLine.m_origin'][0])[2]; sp=struct.unpack_from('<Q',T['rec'],L['CurveElem.m_sketchPlaneId'][0])[0]
    tr=struct.unpack_from('<3I',T['row'],8)
    man=[]
    for (p0,p1) in segs:
        nid=g.nextid; g.nextid+=1
        hd,rec,it,row=genlib.make_line(g,T,nid,sp,p0,p1,zt,tr,Tsp=sp)
        g.new.append((hd,rec,it,nid)); g.rows.append(row); man.append((nid,p0,p1))
    g.itag=T['item'][W+8:W+10]
    g.commit(a.out)
    json.dump(man,open(a.manifest or a.out+'.json','w'))
    print('generated',len(man),'segments ->',a.out)
if __name__=="__main__": main()
