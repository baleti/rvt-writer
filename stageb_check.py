#!/usr/bin/env python3
"""stageb_check.py GT_TSV MANIFEST : compare Revit's export (gt_geom tsv) of a writer-built file with the manifest expectations.
columns: [id,x,y] -> FINST transform origin ~ (x,y,0), solid G row with volume > 0"""
import sys,json,re
tsv,man=sys.argv[1:3]; M=json.load(open(man)); bad=0
rows=[l.rstrip('\n').split('\t') for l in open(tsv,errors='replace')]
el={r[1]:r for r in rows if r[0]=='EL'}; fin={r[1]:r for r in rows if r[0]=='FINST'}
vol={}
for r in rows:
    if r[0]=='G': vol.setdefault(r[1].split('.')[0],0); vol[r[1].split('.')[0]]+=float(r[2].split('=')[1])
for cls,items in M.items():
    if cls in ('names','edited','deleted','renames','rephased'): continue
    if cls=='room_requests':
        for it in items:
            nm,num=it[3],it[4]; rr=[r for r in rows if r[0]=='ROOM' and r[5]=='number='+num]
            ok=bool(rr) and float(rr[0][2][5:])>0.9*it[5]*it[6]*0.9 and any(e2[2]=='Room' and nm in e2[4] for e2 in el.values() if e2[1]==rr[0][1])
            if not ok: print('BAD room request',it,rr[:1]); bad+=1
        continue
    if cls=='shifted':
        import os
        yr=tsv.split('/')[-1][:4]
        def grows(rr,i):
            out=[]
            for r in rr:
                if r[0]=='G' and r[1].split('.')[0]==i:
                    try: v=float(r[2].split('=')[1]); c=[float(x) for x in r[4].split('=')[1].split(',')]
                    except Exception: continue
                    out.append((v,c))
            return out
        def origins(rr,i): return [tuple(float(v) for v in re.search(r'transform=([^;]*)',r[4]).group(1).split(',')) for r in rr if r[0]=='I' and r[1]==i and 'transform=' in r[4]]
        key=lambda q:(round(q[0],6),round(q[1][0],4),round(q[1][1],4),round(q[1][2],4))
        for it in items:
            L=lambda t: [l.rstrip('\n').split('\t') for l in open(os.path.expanduser('~/rvt-research/gt_geom/%s_%s_%s.tsv'%(yr,it[1],t)),errors='replace')]
            base,var=L('base'),L('var'); nsol=0; moved=0; fixed=0; instn=0; DX,DY=100.0,50.0
            for tid,nid in zip(it[5],it[4]):
                a_=grows(base,str(tid)); v_=grows(var,str(tid)); bb=list(grows(rows,str(nid))); nsol+=len(a_); ok=len(a_)==len(bb)
                rem_v=list(v_)
                for x in a_:
                    # does this base solid move in the rosetta variant (+100,+50)? then the copy must move by (dx,dy), else it must stay
                    jv=next((j for j,y in enumerate(rem_v) if abs(x[0]-y[0])<1e-6*max(1,abs(x[0])) and abs(x[1][0]+DX-y[1][0])<1e-3 and abs(x[1][1]+DY-y[1][1])<1e-3 and abs(x[1][2]-y[1][2])<1e-3),None)
                    mv=jv is not None
                    if mv: rem_v.pop(jv)
                    ex=(x[1][0]+(it[2] if mv else 0),x[1][1]+(it[3] if mv else 0),x[1][2])
                    j=next((j for j,y in enumerate(bb) if abs(x[0]-y[0])<1e-6*max(1,abs(x[0])) and abs(ex[0]-y[1][0])<1e-3 and abs(ex[1]-y[1][1])<1e-3 and abs(ex[2]-y[1][2])<1e-3),None)
                    if j is None: ok=False; break
                    bb.pop(j); moved+=mv; fixed+=(not mv)
                if not ok: print('BAD shifted solids',it[1],'tpl',tid,'new',nid); bad+=1
                ob,ov,oc=origins(base,str(tid)),origins(var,str(tid)),origins(rows,str(nid)); instn+=len(ob)
                ex=[(o[0]+(it[2] if abs(w[0]-o[0]-DX)<1e-4 else 0),o[1]+(it[3] if abs(w[1]-o[1]-DY)<1e-4 else 0),o[2]) for o,w in zip(ob,ov)]
                if len(ex)!=len(oc) or any(max(abs(p-q) for p,q in zip(e1,c1))>1e-4 for e1,c1 in zip(sorted(ex),sorted(oc))): print('BAD shifted instance transforms',it[1],'tpl',tid,'new',nid,sorted(ex)[:2],sorted(oc)[:2]); bad+=1
            print('shifted',it[1],(it[2],it[3]),'elements',len(it[4]),'solids',nsol,'(moved %d, local-frame %d)'%(moved,fixed),'instance transforms',instn)
        continue
    for it in items:
        i=str(it[0]); e=el.get(i)
        if not e and len(it)>1 and it[1] in ('Viewport','nolist'): continue
        if not e: print('MISSING',cls,i); bad+=1; continue
        if cls=='columns':
            o=[float(v) for v in re.search(r'transform=([^;]*)','\t'.join(fin[i])).group(1).split(',')] if i in fin else None
            ok=e[2]=='FamilyInstance' and (cls!='columns' or e[3]=='Structural Columns') and o and abs(o[0]-it[1])<1e-6 and abs(o[1]-it[2])<0.25 and vol.get(i,0)>0 and (len(it)<6 or e[5]=='level=%d'%it[5])
            if not ok: print('BAD column',i,e[2:5],o,vol.get(i)); bad+=1
        if cls in('windows','doors'):
            if len(it)>3 and e[4]!=it[3]: print('BAD type name',i,e[3:5],it); bad+=1
            o=[float(v) for v in re.search(r'transform=([^;]*)','\t'.join(fin[i])).group(1).split(',')] if i in fin else None
            ok=e[2]=='FamilyInstance' and o and abs(o[0]-it[1])<1e-6 and abs(o[1]-it[2])<0.25 and vol.get(i,0)>0
            if not ok: print('BAD',cls,i,e[2:5],o,vol.get(i)); bad+=1
            # Revit's bounding box must contain the requested point (catches cached outlines far from the host wall, 2026-10-15 door bug)
            bb=[r for r in rows if r[0]=='BB' and r[1]==i]
            if bb:
                lo=[float(v) for v in bb[0][2].split(',')]; hi=[float(v) for v in bb[0][3].split(',')]
                if not (lo[0]-0.5<=it[1]<=hi[0]+0.5 and lo[1]-0.5<=it[2]<=hi[1]+0.5): print('BAD bbox',cls,i,'requested',it[1:3],'bbox',lo,hi); bad+=1
        if cls=='rooms':      # writer rooms: [id,name,number,level,W,D]; Revit's area (to the wall faces) must be close to W*D, never 0
            rr=[r for r in rows if r[0]=='ROOM' and r[1]==i]
            a=float(rr[0][2].split('=')[1]) if rr else 0.0
            if not (0.75*it[4]*it[5]<=a<=1.0001*it[4]*it[5]): print('BAD room area',i,it,'revit area',a); bad+=1
            else: print('room',i,it[1],'area',round(a,3),'of',it[4]*it[5])
        if cls=='textnotes':
            t=[r for r in rows if r[0]=='TEXT' and r[1]==i]
            ok=bool(t) and t[0][2]==it[3] and abs(float(t[0][3].split(',')[0])-it[1])<1e-6 and abs(float(t[0][3].split(',')[1])-it[2])<1e-6
            if not ok: print('BAD textnote',i,t[:1],it); bad+=1
        if cls=='roofs':      # free-size roof [id,x0,y0,W,D]: Revit's bounding box must be the requested rectangle (flat footprint roof, eaves 0), volume positive
            bb=[r for r in rows if r[0]=='BB' and r[1]==i]
            ok=e[2] in ('ProfileRoof','FootPrintRoof','Roof') and vol.get(i,0)>0 and bool(bb)
            if bb:
                lo=[float(v) for v in bb[0][2].split(',')]; hi=[float(v) for v in bb[0][3].split(',')]
                ok=ok and abs(lo[0]-it[1])<0.05 and abs(lo[1]-it[2])<0.05 and abs(hi[0]-it[1]-it[3])<0.05 and abs(hi[1]-it[2]-it[4])<0.05 and (len(it)<6 or abs(lo[2]-it[5])<0.05)
            if not ok: print('BAD roof',i,e[2:5],it,bb[:1],vol.get(i)); bad+=1
            else: print('roof',i,it[1:],'bbox ok volume',round(vol.get(i,0),2))
        if cls=='floors':
            ok=e[2]=='Floor' and (len(it)<6 or e[5]=='level=%d'%it[5]) and abs(vol.get(i,0)-it[3]*it[4]*0.4921259842519685)<1e-3*it[3]*it[4]
            if not ok: print('BAD floor',i,e[2:5],vol.get(i),it[3]*it[4]*0.4921259842519685); bad+=1
        if cls=='walls':
            w=[r for r in rows if r[0]=='WALLLOC' and r[1]==i]
            m=re.findall(r'(-?[0-9.eE+-]+),(-?[0-9.eE+-]+),(-?[0-9.eE+-]+)',w[0][2]) if w else []
            ok=len(m)>=2 and abs(float(m[0][0])-it[1])<1e-6 and abs(float(m[0][1])-it[2])<1e-6 and abs(float(m[1][0])-it[3])<1e-6 and abs(float(m[1][1])-it[4])<1e-6 and vol.get(i,0)>0
            pi=[r for r in rows if r[0]=='PINST' and r[1]==i]
            if len(it)>8 and (it[8] or it[9]): ok=ok and bool(pi) and pi[0][2]=='Mark='+(it[8] or '') and pi[0][3]=='Comments='+(it[9] or '')
            if len(it)>11 and it[11]:
                full=((it[3]-it[1])**2+(it[4]-it[2])**2)**0.5*it[5]*0.65616797900262469; ok=ok and vol.get(i,0)<0.99*full
                if not ok: print('NOT CUT',i,vol.get(i),full)
            if len(it)>10 and it[10]:
                ps={r[2]:r for r in rows if r[0]=='PSHARED' and r[1]==i}
                for nm,vv in it[10].items():
                    r=ps.get(nm)
                    if not r: ok=False; continue
                    gv=r[4]; 
                    try: ok=ok and abs(float(gv)-float(vv))<1e-9
                    except Exception: ok=ok and gv==str(vv)
            if not ok: print('BAD wall',i,w[:1],it,vol.get(i)); bad+=1
        if cls=='levels':
            ok=e[2]=='Level' and e[4]==it[1]
            if not ok: print('BAD level',i,e[2:5],it); bad+=1
        if cls=='views':
            ok=e[2]=='ViewPlan' and e[4]==it[1]
            if not ok: print('BAD view',i,e[2:5],it); bad+=1
        if cls=='sheets':
            ok=e[2]=='ViewSheet' and e[4]==it[1]
            if not ok: print('BAD sheet',i,e[2:5],it); bad+=1
        if cls=='rooms':
            rr=[r for r in rows if r[0]=='ROOM' and r[1]==i]
            ok=e[2]=='Room' and it[1] in e[4] and bool(rr) and rr[0][2].startswith('area=') and abs(float(rr[0][2][5:])-(it[4]-0.4544)*(it[5]-0.4544))<0.002*it[4]*it[5] and rr[0][5]=='number='+it[2]
            if not ok: print('BAD room',i,e[2:5],it); bad+=1
        if cls=='grids':
            gr=[r for r in rows if r[0]=='GRID' and r[1]==i]
            m=re.findall(r'(-?[0-9.eE+-]+),(-?[0-9.eE+-]+),(-?[0-9.eE+-]+)',gr[0][3]) if gr else []
            ok=e[2]=='Grid' and bool(gr) and gr[0][2]=='name='+it[1] and len(m)>=2 and max(abs(float(m[0][0])-it[2][0]),abs(float(m[0][1])-it[2][1]),abs(float(m[1][0])-it[3][0]),abs(float(m[1][1])-it[3][1]))<1e-6
            if not ok: print('BAD grid',i,e[2:5],gr[:1],it); bad+=1
        if cls=='topos':
            tp=[r for r in rows if r[0]=='TOPO' and r[1]==i]
            pts=[tuple(float(v) for v in q.split(',')) for q in tp[0][2][len('points='):].split(';')] if tp else []
            ok=e[2]=='TopographySurface' and len(pts)==5 and any(abs(p[0]-it[1])<1e-6 and abs(p[1]-it[2])<1e-6 for p in pts)
            if not ok: print('BAD topo',i,e[2:5],pts[:2],it); bad+=1
print('CHECK',tsv.split('/')[-1],'ids',sum(len(v) for v in M.values()),'bad',bad); sys.exit(1 if bad else 0)
