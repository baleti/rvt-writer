import sys,os,glob
sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
from rosetta_features import F
R=os.path.expanduser('~/rvt-research/rosetta'); G=os.path.expanduser('~/rvt-research/gt_geom')
L=["# Rosetta files (session 181, Revit API oracle)","",
"Each feature = one tiny file made in the real Revit (seed = Revit-saved template `ds0.rte`, 2024) containing ONE known object, plus a variant where exactly one parameter value changed.",
"Files: `<year>_<feature>_base.rte` / `_var.rte`; Revit's own geometry for each is in `~/rvt-research/gt_geom/<year>_<feature>_{base,var}.tsv` (format: gt_geom/FORMAT.md).",
"Seed level ids: Level 1 = 355, Level 2 = 2607 (elevation per the seed template). Units: feet. Everything else in the file is the unmodified template, so DIFF base vs var (and base vs ds0.rte) to isolate the object's records.","",
"| feature | present | exact construction (base; variant change) |","|---|---|---|"]
for k,(d,_) in F.items():
    have=['%s:%s'%(y,'+'.join(v for v in ('base','var') if os.path.exists('%s/%d_%s_%s.rte'%(R,y,k,v)))) for y in (2024,2026)]
    have=[h for h in have if not h.endswith(':')]
    L.append("| %s | %s | %s |"%(k,' '.join(have) or 'failed/pending (see LOG)',d))
open(R+'/README.md','w').write('\n'.join(L)+'\n'); print(len(L))
