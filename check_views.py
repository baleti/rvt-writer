#!/usr/bin/env python3
"""check_views.py MANIFEST VIEWS : compare a writer manifest's viewports / detail lines / view text notes with Revit's viewdump (gt_views .views file).
viewport: VIEWPORT row with sheet+view as written; centre delta vs requested is reported (requested centre assumes the given model centre).
detail line: OWNED row in the plan, DetailLine, endpoints equal. view text: OWNED TextNote in the plan, text + x,y equal."""
import sys,json
M=json.load(open(sys.argv[1])); rows=[l.rstrip('\n').split('\t') for l in open(sys.argv[2],errors='replace')]; bad=0; n=0
vp={r[1]:r for r in rows if r[0]=='VIEWPORT'}; own={r[2]:r for r in rows if r[0]=='OWNED'}
kv=lambda r: dict(x.split('=',1) for x in r if '=' in x)
for i,_,sheet,plan,c in M.get('viewports',[]):
    n+=1; r=vp.get(str(i))
    if not r: print('MISSING viewport',i); bad+=1; continue
    d=kv(r); ok=d['sheet']==str(sheet) and d['view']==str(plan)
    cc=[float(v) for v in d['center'].split(',')]; print('viewport',i,'sheet',d['sheet'],'view',d['view'],'centre',cc[:2],'requested',c,'delta %.3f,%.3f ft'%(cc[0]-c[0],cc[1]-c[1]))
    if not ok: print('BAD viewport',i,r[:4]); bad+=1
for i,_,plan,p0,p1 in M.get('detail_lines',[]):
    n+=1; r=own.get(str(i))
    ok=bool(r) and r[1]==str(plan) and r[3]=='DetailLine'
    if ok:
        pts=kv(r)['curve'].split(' ')[1:3]; a=[float(v) for v in pts[0].split(',')]; b=[float(v) for v in pts[1].split(',')]
        ok=max(abs(a[0]-p0[0]),abs(a[1]-p0[1]),abs(b[0]-p1[0]),abs(b[1]-p1[1]))<1e-6
    if not ok: print('BAD detail line',i,r); bad+=1
for i,_,plan,x,y,t in M.get('view_texts',[]):
    n+=1; r=own.get(str(i))
    ok=bool(r) and r[1]==str(plan) and r[3]=='TextNote'
    if ok:
        d=kv(r); cc=[float(v) for v in d['coord'].split(',')]; ok=d['text']==t and abs(cc[0]-x)<1e-6 and abs(cc[1]-y)<1e-6
    if not ok: print('BAD view text',i,r); bad+=1
print('VIEWCHECK items',n,'bad',bad); sys.exit(1 if bad else 0)
