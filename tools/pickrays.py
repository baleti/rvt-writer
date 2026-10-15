#!/usr/bin/env python3
"""tools/pickrays.py WALLS.txt-or-manifest  -> ray string: one ray per wall through its midpoint, perpendicular, at mid height. rows: id x0 y0 x1 y1 h z0"""
import sys,math
def rays(rows):
    out=[]
    for i,x0,y0,x1,y1,h,z0 in rows:
        dx,dy=x1-x0,y1-y0; L=math.hypot(dx,dy); 
        if L<1e-6: continue
        nx,ny=-dy/L,dx/L; mx,my=(x0+x1)/2,(y0+y1)/2
        out.append('%.4f,%.4f,%.3f,%.5f,%.5f'%(mx-nx*6,my-ny*6,z0+h/2,nx,ny))
    return ';'.join(out)
if __name__=='__main__':
    rows=[]
    for l in open(sys.argv[1]):
        p=l.split()
        if p and p[0]=='W': rows.append((int(p[1]),)+tuple(float(v) for v in p[3:7])+(float(p[7]),0.0))
    print(rays(rows))
