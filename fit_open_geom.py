import sys,os,re,json,struct,collections; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,fitgen
Y=2024; tag='walls_open_geom_base'
g=rvtgen.Gen(os.path.expanduser('~/rvt-research/rosetta/%d_%s.rte'%(Y,tag)))
rows=[l.rstrip('\n').split('\t') for l in open(os.path.expanduser('~/rvt-research/gt_geom/%d_%s.tsv'%(Y,tag)),errors='replace')]
walls=[int(r[1]) for r in rows if r[0]=='EL' and r[2]=='Wall']
fin={r[1]:[float(v) for v in re.search(r'transform=([^;]*)',' '.join(r)).group(1).split(',')] for r in rows if r[0]=='FINST'}
cat={r[1]:r[3] for r in rows if r[0]=='EL'}
wins=[(int(i),xyz) for i,xyz in fin.items() if cat.get(i)=='Windows']
Hs=[10,12,9,14,10,11]
by=collections.defaultdict(list)
for n,w in enumerate(walls):
    t=g.template(w); wl=[r for r in rows if r[0]=='WALLLOC' and r[1]==str(w)][0]
    m=re.findall(r'(-?[0-9.eE+-]+),(-?[0-9.eE+-]+),(-?[0-9.eE+-]+)',wl[2]); sx,sy,ex,ey=float(m[0][0]),float(m[0][1]),float(m[1][0]),float(m[1][1])
    # window of this wall: nearest window origin to the 0.4 point
    wx0,wy0=sx+(ex-sx)*0.4,sy+(ey-sy)*0.4
    wi=min(wins,key=lambda a:(a[1][0]-wx0)**2+(a[1][1]-wy0)**2)
    L=((ex-sx)**2+(ey-sy)**2)**.5; H=Hs[n//4]; q=n%4
    f={'1':1.0,'sx':sx,'sy':sy,'ex':ex,'ey':ey,'L':L,'H':H,'wx':wi[1][0],'wy':wi[1][1],'hp':0.4*L,'LH':L*H,'hpH':0.4*L*H,'H2':H*H,'L2':L*L}
    by[q].append((w,t,f,wi[0]))
out={}
import genlib2
for q,lst in sorted(by.items()):
    # window fits per direction
    wt=[g.template(i) for w,t,f,i in lst]; wf=[{'1':1.0,'x':f['wx'],'y':f['wy'],'z':3.0,'hp':f['hp'],'sx':f['sx'],'sy':f['sy'],'L':f['L']} for w,t,f,i in lst]
    out['win%d'%q]={}
    for key in ('rec','item'):
        r=fitgen.fit_samples([t[key] for t in wt],wf,maxterms=3); out['win%d'%q][key]=r; print('  win',q,key,'fitted',len(r['found']) if r else None,'unexpl',len((r or {}).get('unexpl',[])),'lens',sorted({len(t['rec']) for t in wt}))
for q,lst in sorted(by.items()):
    print('dir',q,'samples',len(lst),'rec lens',sorted({len(t['rec']) for w,t,f,i in lst}))
    out[str(q)]={}
    for key in ('rec','item','hdr'):
        r=fitgen.fit_samples([t[key] for w,t,f,i in lst],[f for w,t,f,i in lst],maxterms=3); out[str(q)][key]=r
        print('  ',key,'fitted',len(r['found']) if r else None,'unexpl',len((r or {}).get('unexpl',[])))
json.dump(out,open(os.path.expanduser('~/rvt-research/write-lab/files/openfit_geom.json'),'w'))
