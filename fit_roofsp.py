#!/usr/bin/env python3
"""fit_roofs.py YEAR : fit the 24-record roof+ceiling group of rosetta <year>_roofs12_{base,var} (12 rectangles on level 1; var = same on level z=12)
-> files/rooffit_<year>.json {role: {rec/hdr/item: fit}} + z slopes. Run on host1 (h1run, CPU minutes)."""
import sys,os,re,json,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,fitgen,genlib2
Y=int(sys.argv[1]); R=os.path.expanduser('~/rvt-research/rosetta/%d_roofs12p_%s.rte')
R12=[(60,-100,26,40),(110,-100,20,30),(150,-100,24,25),(60,-150,10,50),(120,-150,18,36),(170,-150,12,20),(60,-200,30,44),(115,-200,27,28),(150,-200,15,60),(220,-200,9,18),(220,-100,21,33),(220,-150,13,26)]
log=open(os.path.expanduser('~/rvt-research/write-lab/pipeline/logs/%s_roofs12p_%d.sh.log'%({2024:'1300',2026:'1301'}[Y],Y))).read()
def firsts(lab):
    line=[l for l in log.splitlines() if l.startswith('roofs12p %s created'%lab)][0]
    return [int(m) for m in re.findall(r' R\d+=(\d+)/',line)], [int(x) for x in re.search(r'copied=([\d,]+)',line).group(1).split(',')]
gb=rvtgen.Gen(R%(Y,'base')); gv=rvtgen.Gen(R%(Y,'var'))
fb,cp=firsts('base'); fv,_=firsts('var'); n=fb[1]-fb[0]; assert all(fb[k+1]-fb[k]==n for k in range(11))
out={'n':n,'first':fb[0],'copied':cp,'roles':{}}
for r in range(n):
    KS=[k for k in range(12) if R12[k][2]!=R12[k][3]]          # square roofs are a different regime (W==D)
    try: Ts=[gb.template(fb[k]+r) for k in KS]
    except IndexError: print('role',r,'missing (id gap)'); continue
    feats=[dict(genlib2._ffeats(x0,y0,W,D),W2=W*W,D2=D*D,diag=(W*W+D*D)**0.5) for x0,y0,W,D in [R12[k] for k in KS]]
    role={'cls':Ts[0]['cls']}
    for key in ('rec','hdr','item'):
        L=[len(t[key]) for t in Ts]
        if len(set(L))!=1: role[key]={'lens':L}; continue
        role[key]=fitgen.fit_samples([t[key] for t in Ts],feats,maxterms=3)
        if role[key] and role[key]['unexpl']:
            names=list(feats[0]); ext=[dict(f,**{a+'*'+b:f[a]*f[b] for i_,a in enumerate(names) for b in names[i_:] if a!='1' and b!='1'}) for f in feats]
            al=[o for o in role[key]['unexpl'] if o%8==0 or True]
            r2=fitgen.fit_samples([t[key] for t in Ts],ext,maxterms=3,offsets=al)
            role[key]['found'].update(r2['found']); role[key]['unexpl']=r2['unexpl']
    # z slope: var group 0 (level z=12) vs base group 0
    tv=gv.template(fv[0]+r); sl={}
    for key in ('rec','hdr','item'):
        a,b=Ts[0][key],tv[key]
        if len(a)!=len(b): sl[key]='len'; continue
        sl[key]={o:round((struct.unpack_from('<d',b,o)[0]-struct.unpack_from('<d',a,o)[0])/12.0,10) for o in range(len(a)-7) if a[o:o+8]!=b[o:o+8] and abs(struct.unpack_from('<d',b,o)[0]-struct.unpack_from('<d',a,o)[0]-12.0)<1e-6}
        sl[key+'_diffbytes']=[o for o in range(len(a)) if a[o]!=b[o]][:60]
    role['zslope']=sl; out['roles'][r]=role
    print(r,role['cls'],{k:(len(role[k]['found']),len(role[k]['unexpl'])) if isinstance(role[k],dict) and 'found' in role[k] else role[k] for k in ('rec','hdr','item')},flush=True)
json.dump(out,open(os.path.expanduser('~/rvt-research/write-lab/files/rooffit3p_%d.json'%Y),'w'))
