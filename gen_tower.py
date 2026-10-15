#!/usr/bin/env python3
"""gen_tower.py - parametric twisting tower: N generated Levels (spacing law), one sketch plane per level and a regular n-gon floor outline of model lines per level
(radius law + twist per level). Everything is produced with my own writer on top of a Revit-saved 2024 .rte seed (ds0.rte). Deterministic (--seed only perturbs radius jitter)."""
import sys,struct,math,argparse,json,random; sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import rvtgen,genlib
from gen_levels import elevations,latest_patch
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--year',type=int,default=2024,choices=[2024,2026]); ap.add_argument('--seed-file'); ap.add_argument('--level-template'); ap.add_argument('--line-template')
    ap.add_argument('--levels',type=int,default=12); ap.add_argument('--spacing',default='golden',choices=['linear','golden','sine','setback']); ap.add_argument('--step',type=float,default=12.0); ap.add_argument('--start',type=float,default=40.0)
    ap.add_argument('--sides',type=int,default=6); ap.add_argument('--r0',type=float,default=40.0); ap.add_argument('--r-law',default='waist',choices=['const','waist','taper','bulge'])
    ap.add_argument('--twist',type=float,default=7.0,help='degrees per level'); ap.add_argument('--jitter',type=float,default=0.0); ap.add_argument('--seed',type=int,default=1)
    ap.add_argument('--out',required=True)
    a=ap.parse_args(); rnd=random.Random(a.seed)
    cfg={2024:('files/ds0.rte','files/ds3b.rte','files/k_line.rte'),2026:('files/o26_line.rte','files/o26_lv1.rte','files/o26_line.rte')}[a.year]
    a.seed_file=a.seed_file or cfg[0]; a.level_template=a.level_template or cfg[1]; a.line_template=a.line_template or cfg[2]
    gL=rvtgen.Gen(a.level_template); tlid=max(gL.e.m.ids); TL=gL.template(tlid)
    gl=rvtgen.Gen(a.line_template); lid=max(gl.e.m.ids); TS=gl.template(lid-1); TLn=gl.template(lid); TSID=lid-1
    g=rvtgen.Gen(a.seed_file)
    et=g._et(); n_=struct.unpack_from('<I',et,2)[0]
    best=max(range(n_),key=lambda k:(struct.unpack_from('<I',et,6+40*k+12)[0],struct.unpack_from('<I',et,6+40*k+8)[0]))
    ea,eb,_=struct.unpack_from('<3I',et,6+40*best+8); tr=(ea,eb,eb)
    elev=elevations(a.spacing,a.levels,a.step,a.start); man={'levels':[],'planes':[],'lines':[]}
    def R(k):
        t=k/max(1,a.levels-1)
        f={'const':1.0,'waist':1.0-0.35*math.sin(math.pi*t),'taper':1.0-0.6*t,'bulge':1.0+0.4*math.sin(math.pi*t)}[a.r_law]
        return a.r0*f*(1+a.jitter*(rnd.random()-0.5))
    lvl_ids=[]
    for k,z in enumerate(elev):
        nid=g.nextid; g.nextid+=1; lvl_ids.append(nid); name='T%02d'%(k+1)
        hd,rec,it,row=genlib.make_level(g,TL,nid,name,z,tr); g.new.append((hd,rec,it,nid)); g.rows.append(row); man['levels'].append((nid,name,z))
    for k,z in enumerate(elev):
        nid=g.nextid; g.nextid+=1
        hd,rec,it,row=genlib.make_sketchplane(g,TS,nid,lvl_ids[k],z,tr); g.new.append((hd,rec,it,nid)); g.rows.append(row); man['planes'].append((nid,lvl_ids[k],z))
    for k,z in enumerate(elev):
        sp=man['planes'][k][0]; r=R(k); th=math.radians(a.twist*k)
        pts=[(r*math.cos(th+2*math.pi*i/a.sides),r*math.sin(th+2*math.pi*i/a.sides)) for i in range(a.sides)]
        for i in range(a.sides):
            p0=pts[i]; p1=pts[(i+1)%a.sides]
            nid=g.nextid; g.nextid+=1
            hd,rec,it,row=genlib.make_line(g,TLn,nid,sp,p0,p1,z,tr,Tsp=TSID); g.new.append((hd,rec,it,nid)); g.rows.append(row); man['lines'].append((nid,sp,p0,p1,z))
    g.itag=TL['item'][8+8:8+10]
    g.latest_edits=[('Latest',lambda raw: latest_patch(raw,lvl_ids,a.year))]
    g.commit(a.out); json.dump(man,open(a.out+'.json','w'))
    print('generated',len(man['levels']),'levels',len(man['planes']),'sketch planes',len(man['lines']),'lines ->',a.out)
if __name__=="__main__": main()
