import sys,os,struct,json,collections; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,fitgen
Y=int(sys.argv[1]) if len(sys.argv)>1 else 2024
g=rvtgen.Gen(os.path.expanduser('~/rvt-research/rosetta/%d_view_regions_fit_var.rte'%Y)); b=rvtgen.Gen(os.path.expanduser('~/rvt-research/rosetta/%d_view_regions_fit_base.rte'%Y))
new=sorted(set(g.e.m.ids)-set(b.e.m.ids)); cls={i:g.template(i)['cls'] for i in new}
body=[i for i in new if cls[i]!='LinearDimString']; lds=[i for i in new if cls[i]=='LinearDimString']
R=[(14,9,3,2),(2,2,4,3),(8,2,2,6),(3,8,6,2),(15,2,2.5,2.5),(10,10,5,3),(1,5,1,1),(6,6,7,2)]
feats=[dict(x=x,y=y,w=w,d=d,x2=x+w,y2=y+d,one=1.0,area=w*d,perim=2*(w+d),cx=x+w/2,cy=y+d/2) for x,y,w,d in R]
roles={}
for k in range(8):
    grp=body[7*k:7*k+7]; assert [cls[i] for i in grp]==['SketchPlane','VarSketch','FilledRegion']+['CurveElem']*4,[cls[i] for i in grp]
    for r,i in enumerate(grp): roles.setdefault(r,[]).append(i)
    for r,i in enumerate(lds[2*k:2*k+2]): roles.setdefault(7+r,[]).append(i)
out={}
for r,ids in sorted(roles.items()):
    T=[g.template(i) for i in ids]
    for key in ('rec','item','hdr'):
        res=fitgen.fit_samples([t[key] for t in T],feats,maxterms=3)
        out['%d.%s'%(r,key)]=res
        print(r,cls[ids[0]],key,'fit',len(res['found']) if res else None,'unexpl',(res or {}).get('unexpl',[])[:12])
json.dump(out,open('files/regfit_%d.json'%Y,'w'))
