import sys,os,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen
R=os.path.expanduser('~/rvt-research/rosetta/')
A=rvtgen.Gen(R+'2026_view_sheet_base.rte'); B=rvtgen.Gen(R+'2026_view_sheet_var.rte')
for tid in range(303689,303712):
    try: a=A.template(tid); b=B.template(tid)
    except Exception as e: continue
    for key in ('rec','item','hdr'):
        x,y=a[key],b[key]
        if x!=y:
            d=[i for i in range(min(len(x),len(y))) if x[i]!=y[i]]
            print(tid,a['cls'],key,len(x),len(y),'bytes',d[:16],flush=True)
            names=[(n,o,e) for n,o,e,v in a['log'] if key=='rec' and any(o<=q<e for q in d[:16])]
            la={n:v for n,o,e,v in a['log']}; lb={n:v for n,o,e,v in b['log']}
            for k in la:
                if k in lb and str(la[k])!=str(lb[k]) and 'Identifier' not in k and k!='ElementId.m_id': print('   ',k,la[k],'->',lb[k],flush=True)
