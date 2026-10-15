#!/usr/bin/env python3
"""tools/fit_joinwalls.py YEAR : fit the 4 JOINED walls of a Revit-made rectangle (rosetta rooms_lv base+var: 8 rectangles x 2 = 16 samples per wall role)
as linear functions of the rectangle features (genlib2._rfeats). Output files/joinwallfit_<YEAR>.json: per role {tpl id, rec/hdr/item fits}, and the
id roles of rectangle 0 (walls, level, room, plan) used to remap references when cloning."""
import sys,os,json; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,fitgen,wledit,genlib2,scenes
Y=int(sys.argv[1]); R=os.path.expanduser('~/rvt-research/rosetta/')
RECT=[(0,0,20,12),(5,5,14,9),(10,0,25,10),(0,8,16,16),(30,30,12,8),(2,2,30,12),(0,0,11,7),(20,10,18,13)]
base=set(wledit.Editor(scenes.WL+'/'+scenes.SEEDF[Y]).m.ids)
S={}
for v,f in ((0,'base'),(1,'var')):
    g=rvtgen.Gen(R+'%d_rooms_lv_%s.rte'%(Y,f)); new=sorted(set(g.e.m.ids)-base); T={i:g.template(i) for i in new}
    S[v]=dict(T=T,walls=[i for i in new if T[i]['cls']=='SWall'],lv=[i for i in new if T[i]['cls']=='Level'],
              room=[i for i in new if T[i]['cls']=='RoomElem'],plan=[i for i in new if T[i]['cls']=='LevelRoomPlan'])
    assert len(S[v]['walls'])==32
assert S[0]['walls']==S[1]['walls'],'base/var wall ids differ'
out={'year':Y,'roles':[],'ids':{'walls':S[0]['walls'][:4],'level':S[0]['lv'][0],'room':S[0]['room'][0],'plan':S[0]['plan'][0]},
     'all_walls':S[0]['walls'],'all_levels':S[0]['lv'],'all_rooms':S[0]['room'],'all_plans':S[0]['plan']}
for role in range(4):
    blobs={'rec':[],'hdr':[],'item':[]}; feats=[]
    for v in (0,1):
        for k,(x0,y0,W,D) in enumerate(RECT):
            if str(k) in os.environ.get('EXCL','').split(','): continue
            t=S[v]['T'][S[v]['walls'][4*k+role]]
            for key in blobs: blobs[key].append(t[key])
            feats.append(genlib2._rfeats(x0+3*v,y0,W,D,10.0*k+10))
    r={'tpl':S[0]['walls'][role]}
    for key in blobs:
        fr=fitgen.fit_samples(blobs[key],feats,maxterms=3); r[key]=fr
        print('role',role,key,'len',len(blobs[key][0]),'fitted',len(fr['found']) if fr else None,'unexpl',(fr or {}).get('unexpl',[])[:12],flush=True)
    out['roles'].append(r)
out['excluded_rects']=os.environ.get('EXCL','')
json.dump(out,open(scenes.WL+'/files/joinwallfit_%d%s.json'%(Y,os.environ.get('SUFFIX','')),'w'))
print('wrote files/joinwallfit_%d.json'%Y)
