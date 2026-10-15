#!/usr/bin/env python3
"""specs/make_full.py : writes specs/full_<year>.json (every class the pure writer supports) + specs/full_finish_<year>.json (finishing pass)"""
import json,os
D=os.path.dirname(os.path.abspath(__file__))
def ring(lv,h,pre):
    P=[(60,0),(120,0),(120,30),(60,30)]
    n=['south','east','north','west']
    return [{"id":pre+n[k],"from":list(P[k]),"to":list(P[(k+1)%4]),"level":lv,"height":h} for k in range(4)]
for Y in (2024,2026):
    w=ring('L1',12.0,'')+ring('L2',12.0,'u_')
    w[0].update(mark='W1',comments='main facade',values={"Department":"Facade","FireRatingMin":60,"UValue":0.28,"LoadBearing":1})
    sp={"year":Y,"name":"full_%d"%Y,
     "levels":[{"name":"L2","elevation":12.0},{"name":"L3","elevation":24.0}],
     "params":[{"name":"Department","kind":"text"},{"name":"FireRatingMin","kind":"int"},{"name":"UValue","kind":"number"},{"name":"LoadBearing","kind":"yesno"}],
     "walls":w,
     "floors":[{"x":60,"y":0,"width":60,"depth":30,"level":"L2"},{"x":60,"y":0,"width":60,"depth":30,"level":"L3"}],
     "columns":[{"x":x,"y":y,"base":b,"top":t} for (b,t) in (('L1','L2'),('L2','L3')) for x in (75,90,105) for y in (10,20)],
     "windows":[{"wall":"south","offset":o} for o in (8,16,44,52)]+[{"wall":"u_south","offset":o} for o in (8,16,24,36,44,52)],
     "doors":[{"wall":"south","offset":30}],
     "views":[{"name":"Plan L1","level":"L1"},{"name":"Plan L2","level":"L2"},{"name":"Plan L3","level":"L3"}],
     "sheets":[{"number":"A-101","name":"Ground floor","viewports":[{"view":"Plan L1","centre":[1.2,0.9]}]},
               {"number":"A-102","name":"First floor","viewports":[{"view":"Plan L2","centre":[1.2,0.9]}]},
               {"number":"A-103","name":"Roof","viewports":[{"view":"Plan L3","centre":[1.2,0.9]}]}],
     "text":[{"x":60,"y":-6,"text":"rvt-write full scene: every writer class, no Revit used to build it"}],
     "detail_lines":[{"view":v,"from":[58,-3],"to":[122,-3]} for v in ("Plan L1","Plan L2","Plan L3")],
     "view_text":[{"view":v,"x":62,"y":-9,"text":v+" (writer)"} for v in ("Plan L1","Plan L2","Plan L3")],
     "stairs":[{"offset":[0,0]}],"railings":[{"offset":[0,0]}],"curtain_walls":[{"offset":[0,0]}],
     "roofs":[{"offset":[70,105]}],
     "topography":[{"offset":[130,-60]}],
     "rooms":[{"id":"roof","level":"L3","x":64,"y":4,"width":20,"depth":14,"name":"Roof studio","number":"301"}]}
    if Y==2024: sp["grids"]=[{"name":n,"from":[x,-12],"to":[x,72]} for n,x in (('A',60),('B',75),('C',90),('D',105),('E',120))]
    json.dump(sp,open('%s/full_%d.json'%(D,Y),'w'),indent=1)
    fin={"openings":True,
     "rooms":[{"level":"L1","x":90,"y":15,"name":"Hall","number":"001"},{"level":"L2","x":90,"y":15,"name":"Studio","number":"101"}],
     "grids":[] if Y==2024 else [{"name":n,"from":[x,-12],"to":[x,72]} for n,x in (('A',60),('B',75),('C',90),('D',105),('E',120))],
     "dimensions":[{"view":"Plan L1","walls":["south","north"],"offset":3.0},{"view":"Plan L1","walls":["west","east"],"offset":3.0}],
     "tags":[{"view":"Plan L1","element":"south","at":[90,-1.5]},{"view":"Plan L1","element":"east","at":[122,15]}],
     "text":[{"view":"Plan L1","x":62,"y":-14,"text":"Finished by Revit: openings, rooms, dims, tags"}],
     "detail_lines":[],
     "filled_regions":[{"view":"Plan L1","x":124,"y":0,"w":6,"d":6}],
     "viewports":[]}
    if Y==2026: fin["dimensions"].append({"view":"Plan L1","grids":["A","E"],"offset":4.0})
    json.dump(fin,open('%s/full_finish_%d.json'%(D,Y),'w'),indent=1)
print('ok')
