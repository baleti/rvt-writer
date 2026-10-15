import sys,os,struct,re,json,collections; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,fitgen
tag=sys.argv[1]; Y=2024
f=os.path.expanduser('~/rvt-research/rosetta/%d_%s.rte'%(Y,tag)); g=rvtgen.Gen(f)
rows=[l.rstrip('\n').split('\t') for l in open(os.path.expanduser('~/rvt-research/gt_geom/%d_%s.tsv'%(Y,tag)),errors='replace')]
walls=[int(r[1]) for r in rows if r[0]=='EL' and r[2]=='Wall']
wins=[(int(r[1]),[float(v) for v in re.search(r'transform=([^;]*)',' '.join(r)).group(1).split(',')]) for r in rows if r[0]=='FINST' and any(q[0]=='EL' and q[1]==r[1] and q[3]=='Windows' for q in rows[:0] or [])]
fin={r[1]:[float(v) for v in re.search(r'transform=([^;]*)',' '.join(r)).group(1).split(',')] for r in rows if r[0]=='FINST'}
cat={r[1]:r[3] for r in rows if r[0]=='EL'}
W={}
for i,xyz in fin.items():
    if cat.get(i)=='Windows': W.setdefault(round(xyz[1]),[]).append(xyz[0])
out={}
bygrp=collections.defaultdict(list)
for n,w in enumerate(walls):
    t=g.template(w); L={nm:(o,e,v) for nm,o,e,v in t['log']}
    y=struct.unpack_from('<d',t['rec'],0)[0] if False else None
    # wall y from its location: use WALLLOC row
    wl=[r for r in rows if r[0]=='WALLLOC' and r[1]==str(w)][0]; m=re.findall(r'(-?[0-9.eE+-]+),(-?[0-9.eE+-]+),(-?[0-9.eE+-]+)',wl[2]); y=float(m[0][1])
    xs=sorted(W.get(round(y),[])); bygrp[len(xs)].append((w,t,y,xs))
for k,lst in sorted(bygrp.items()):
    print('k=%d samples %d'%(k,len(lst)))
    feats=[]
    for w,t,y,xs in lst:
        f_={'1':1.0,'y':y}
        for j in range(k): f_['x%d'%(j+1)]=xs[j]
        feats.append(f_)
    out[str(k)]={}
    for key in ('rec','item','hdr'):
        r=fitgen.fit_samples([t[key] for w,t,y,xs in lst],feats,maxterms=3); out[str(k)][key]=r
        print('  ',key,'fitted',len(r['found']) if r else None,'unexplained',(r or {}).get('unexpl',[])[:20])
json.dump(out,open(os.path.expanduser('~/rvt-research/write-lab/files/openfit_%s.json'%tag),'w'))
