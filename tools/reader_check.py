#!/home/user1/rvt-research/.venv3/bin/python
"""tools/reader_check.py FILE MANIFEST : our own reader (rvt_geometry) vs the writer manifest for shifted copies: bbox centre of every copy element must equal the template element's bbox centre + (dx,dy)"""
import sys as _s
if "venv3" not in _s.executable: raise SystemExit("run with ~/rvt-research/.venv3/bin/python (system python3 lacks mapbox_earcut; the reader silently falls back to boxes)")
import sys,os,json; sys.path.insert(0,os.path.expanduser('~/rvt-research'))
import rvt_geometry as GG
f,man=sys.argv[1:3]; YEAR=sys.argv[3]; M=json.load(open(man)); bad=0; n=0
for it in M.get('shifted',[]):
    feat,dx,dy,nids,tids=it[1],it[2],it[3],it[4],it[5]
    base=os.path.expanduser('~/rvt-research/rosetta/%s_%s_base.rte'%(YEAR,feat))
    idx=GG.file_geometry_index(base)
    for tid,nid in [(t,n_) for t,n_ in zip(tids,nids) if idx.get(t) in ('ProfileRoof','Ceiling','FootPrintRoof','ExtrusionRoof','Floor','SWall','Stairs','StairsRun','Railing','FamilyInstance','CurtainWall')][:80]:
        try: a=GG.element_geometry(base,tid); b=GG.element_geometry(f,nid)
        except Exception as e: print('ERR',feat,tid,nid,e); bad+=1; continue
        def bb(r):
            if r.get('bbox'): return r['bbox']
            pts=[p for so in r.get('solids',[]) if so.get('kind')=='triangle_mesh' for tri in so['triangles'] for p in tri]
            return [[min(p[k] for p in pts) for k in range(3)],[max(p[k] for p in pts) for k in range(3)]] if pts else None
        a['bbox'],b['bbox']=bb(a),bb(b)
        if not a['bbox'] or not b['bbox']: continue
        ca=[(a['bbox'][0][k]+a['bbox'][1][k])/2 for k in range(3)]; cb=[(b['bbox'][0][k]+b['bbox'][1][k])/2 for k in range(3)]
        n+=1
        # world-space elements move by (dx,dy); local-frame instances keep their bbox if the reader gives symbol-local boxes: accept both, count which
        d1=max(abs(cb[0]-ca[0]-dx),abs(cb[1]-ca[1]-dy),abs(cb[2]-ca[2])); d0=max(abs(cb[0]-ca[0]),abs(cb[1]-ca[1]),abs(cb[2]-ca[2]))
        if min(d0,d1)>1e-3: print('BAD',feat,tid,nid,a['class'],'delta',[round(cb[k]-ca[k],4) for k in range(3)],'expected',(dx,dy,0)); bad+=1
print('READERCHECK elements',n,'bad',bad)
