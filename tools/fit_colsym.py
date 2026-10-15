#!/home/user1/rvt-research/.venv3/bin/python
"""tools/fit_colsym.py YEAR : fit the hidden per-geometry column symbol ('variant FamilySymbol' that Revit creates for every distinct column z-range and
references from the column's saved graphics) over rosetta cols_lv base+var. Features 1,z0,z1. -> files/colsym_<YEAR>.json
(samples: variant symbol id, z0, z1, template record lengths; fit of rec and item doubles)"""
import sys,os,json,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research')); sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvt_elemmesh as EM, rvtgen, fitgen
Y=int(sys.argv[1]); R=os.path.expanduser('~/rvt-research/rosetta/%d_cols_lv_%s.rte'); G=os.path.expanduser('~/rvt-research/gt_geom/%d_cols_lv_%s.tsv')
T=[]; feats=[]; meta=[]
for v in ('base','var'):
    f=R%(Y,v); cols=[]; bb={}
    for l in open(G%(Y,v),errors='replace'):
        p=l.rstrip('\n').split('\t')
        if p[0]=='EL' and p[2]=='FamilyInstance' and 'Structural Columns' in p[3]: cols.append(int(p[1]))
        if p[0]=='BB': bb[int(p[1])]=([float(x) for x in p[2].split(',')],[float(x) for x in p[3].split(',')])
    d=EM.Doc(f); g=rvtgen.Gen(f); seen={}
    for c in cols:
        fl=d.rec(c)['fields']; geos,inst=EM._geos_f(fl,3)
        if not inst: geos,inst=EM._geos(fl)
        sids=[int(EM._ob(z['m_instanceInfo']).get('m_symbolId')) for z in inst]
        if len(sids)!=1 or c not in bb: print('skip',v,c,sids); continue
        s=sids[0]; z0,z1=bb[c][0][2],bb[c][1][2]
        if s in seen: assert abs(seen[s][0]-z0)<1e-6 and abs(seen[s][1]-z1)<1e-6,(s,seen[s],z0,z1); continue
        seen[s]=(z0,z1); t=g.template(s); T.append(t); feats.append({'1':1.0,'z0':z0,'z1':z1}); meta.append([v,s,z0,z1,len(t['hdr']),len(t['rec']),len(t['item'])])
for m in meta: print(m)
import collections
maj=collections.Counter(len(t['rec']) for t in T).most_common(1)[0][0]; hmaj=collections.Counter(len(t['hdr']) for t in T).most_common(1)[0][0]
keep=[k for k,t in enumerate(T) if len(t['rec'])==maj and len(t['item'])==len(T[0]['item']) and len(t['hdr'])==hmaj]
out={'samples':[meta[k] for k in keep],'len':maj}
for key in ('rec','item','hdr'):
    bl=[T[k][key] for k in keep]
    if len(set(map(len,bl)))>1: print(key,'lengths differ',sorted(set(map(len,bl)))); out[key]=None; continue
    r=fitgen.fit_samples(bl,[feats[k] for k in keep]); out[key]=r; print(key,'fitted',len(r['found']),'unexplained',len(r['unexpl']),r['unexpl'][:20])
json.dump(out,open(os.path.expanduser('~/rvt-research/write-lab/files/colsym_%d.json'%Y),'w'))
