import sys,os,struct,re,json,collections; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,fitgen,wledit
Y=int(sys.argv[1]) if len(sys.argv)>1 else 2024; f=os.path.expanduser('~/rvt-research/rosetta/%d_rooms_lv_base.rte'%Y); g=rvtgen.Gen(f)
base=set(wledit.Editor({2024:'files/ds0.rte',2026:'files/o26_line.rte'}[Y]).m.ids); new=sorted(set(g.e.m.ids)-base)
cls={i:g.template(i)['cls'] for i in new}
print(collections.Counter(cls.values()))
rooms=[i for i in new if cls[i]=='RoomElem']; plans=[i for i in new if cls[i]=='LevelRoomPlan']
R=[(0,0,20,12),(5,5,14,9),(10,0,25,10),(0,8,16,16),(30,30,12,8),(2,2,30,12),(0,0,11,7),(20,10,18,13)]
ZL=[10*k+10 for k in range(8)]
feats=[]
sys.path.insert(0,'.')
import genlib2
for k,(x0,y0,W,D) in enumerate(R): feats.append(genlib2._rfeats(x0,y0,W,D,ZL[k]))
print(len(rooms),len(plans),[len(g.template(i)['rec']) for i in rooms][:8],[len(g.template(i)['rec']) for i in plans][:8])
out={}
for nm,ids in (('room',rooms),('plan',plans)):
    T=[g.template(i) for i in ids]
    for key in ('rec','item','hdr'):
        r=fitgen.fit_samples([t[key] for t in T],feats,maxterms=3); out[nm+'.'+key]=r
        print(nm,key,'fitted',len(r['found']) if r else None,'unexpl',(r or {}).get('unexpl',[])[:20])
json.dump(out,open('files/roomfit.json' if Y==2024 else 'files/roomfit_%d.json'%Y,'w'))
