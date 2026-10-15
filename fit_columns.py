import sys,os,re,json,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,fitgen
Y=int(os.environ.get('YEAR',2024)); SUF='' if Y==2024 else '_%d'%Y
GT=os.path.expanduser('~/rvt-research/gt_geom/%d_cols_lv_base.tsv'%Y); F=os.path.expanduser('~/rvt-research/rosetta/%d_cols_lv_base.rte'%Y)
rows=[l.rstrip('\n').split('\t') for l in open(GT,errors='replace')]
cols=[r[1] for r in rows if r[0]=='EL' and r[2]=='FamilyInstance' and 'Structural Columns' in r[3]]
org={r[1]:[float(v) for v in re.search(r'transform=([^;]*)',' '.join(r)).group(1).split(',')] for r in rows if r[0]=='FINST'}
Z0=[0,10,22,37]; Z1=[10,22,37,47]
g=rvtgen.Gen(F); T=[];feats=[]
for n,i in enumerate(cols):
    t=g.template(int(i)); T.append(t); L0={nm:(o,e,v) for nm,o,e,v in t['log']}; hl={nm:(o,e,v) for nm,o,e,v in t['hlog']}
    x,y,z=struct.unpack_from('<3d',t['rec'],L0['FamilyInstance.m_instOrigin'][0]); z1=struct.unpack_from('<6d',t['hdr'],hl['Outline.m_minmax'][0])[5]
    feats.append({'1':1.0,'x':x,'y':y,'z0':z,'z1':z1,'dz':z1-z})
print(len(cols),'columns; sample z0:',[f['z0'] for f in feats[:4]])
out={}
for key in ('rec','hdr','item'):
    r=fitgen.fit_samples([t[key] for t in T],feats); out[key]=r; print(key,'fitted',len(r['found']) if r else None,'unexplained',(r or {}).get('unexpl'))
# level-id fields: print assoc/top/bottom ids per sample
L={n:(o,e) for n,o,e,_ in T[0]['log']}
for nm in ('Element.m_assocLevelId','FamilyInstance.m_analyticalTopPlaneId','FamilyInstance.m_analyticalBottomPlaneId'):
    print(nm,[struct.unpack_from('<Q',t['rec'],L[nm][0])[0] for t in T[:8]])
json.dump(out,open(os.path.expanduser('~/rvt-research/write-lab/files/colfit%s.json'%SUF),'w'))
