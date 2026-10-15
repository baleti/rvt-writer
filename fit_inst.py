"""fit_inst.py FILE_TAG CATEGORY_SUBSTR OUTJSON : fit hosted/loose FamilyInstance records (rec/item; hdr outline separately) over samples in a rosetta file"""
import sys,os,re,json,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,fitgen
Y=int(os.environ.get('YEAR',2024))
tag,cat,outj=sys.argv[1:4]
GT=os.path.expanduser('~/rvt-research/gt_geom/%d_%s.tsv'%(Y,tag)); F=os.path.expanduser('~/rvt-research/rosetta/%d_%s.rte'%(Y,tag))
ZL={355:0.0,301553:10.0,301554:22.0,301555:37.0}
rows=[l.rstrip('\n').split('\t') for l in open(GT,errors='replace')]
ids=[int(r[1]) for r in rows if r[0]=='EL' and r[2]=='FamilyInstance' and cat in r[3]]
g=rvtgen.Gen(F); T=[]; feats=[]
for i in ids:
    t=g.template(i); T.append(t); L={nm:(o,e,v) for nm,o,e,v in t['log']}; hl={nm:(o,e,v) for nm,o,e,v in t['hlog']}
    x,y,z=struct.unpack_from('<3d',t['rec'],L['FamilyInstance.m_instOrigin'][0]); hp=struct.unpack_from('<d',t['rec'],L['InsertableInst.m_hostParam'][0])[0]
    lv=struct.unpack_from('<Q',t['rec'],L['Element.m_assocLevelId'][0])[0]; lz=ZL.get(lv,0.0)
    feats.append({'1':1.0,'x':x,'y':y,'z':z,'hp':hp,'lz':lz,'zr':z-lz})
import collections
maj=collections.Counter(len(t['rec']) for t in T).most_common(1)[0][0]
keep=[k for k,t in enumerate(T) if len(t['rec'])==maj]; T=[T[k] for k in keep]; feats=[feats[k] for k in keep]; ids=[ids[k] for k in keep]
print(len(ids),cat,'samples; hdr lens',sorted(set(len(t['hdr']) for t in T)),'rec lens',sorted(set(len(t['rec']) for t in T)))
out={}
for key in ('rec','item'):
    r=fitgen.fit_samples([t[key] for t in T],feats); out[key]=r; print(key,'fitted',len(r['found']) if r else None,'unexplained',(r or {}).get('unexpl'))
out['len']=maj
json.dump(out,open(outj,'w'))
