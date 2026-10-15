#!/usr/bin/env python3
"""rosetta.py YEAR [feature,...] : for each feature create the object in the seed template (ds0.rte of that year family) with the Revit API in my overlay VM, save base + variant, export Revit's geometry (gt) for both."""
import sys,os,re,time
WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign'); sys.path.insert(0,WL)
import guest
from rosetta_features import F
year=int(sys.argv[1]);
OVR={'roof_ceiling':'C:\\ProgramData\\Autodesk\\RVT %d\\Templates\\Default_M_ENU.rte'%year}
SEEDUP={k:os.path.expanduser('~/rvt-research/rosetta/%d_house_base.rte'%year) for k in ('roofs12','stair_shift','railing_shift','curtain_shift','roof_shift','grid_house')}
only=sys.argv[2].split(',') if len(sys.argv)>2 else list(F)
PRE='''using Autodesk.Revit.DB; using Autodesk.Revit.DB.Architecture; using Autodesk.Revit.DB.Structure; using System.Linq; using System.Collections.Generic;
public class StairsFailurePreprocessor : IFailuresPreprocessor { public FailureProcessingResult PreprocessFailures(FailuresAccessor a) { return FailureProcessingResult.Continue; } }
var app = UIApp.Application; int v = __V__; string out_ = "";
var d = app.OpenDocumentFile(@"__SEEDPATH__");
var lvAll = new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().ToList(); var l1 = lvAll.FirstOrDefault(x => x.Name == "Level 1") ?? lvAll.OrderBy(x => x.Elevation).First(); var l2 = lvAll.FirstOrDefault(x => x.Name == "Level 2") ?? lvAll.OrderBy(x => x.Elevation).Last();
'''
POST='''
d.SaveAs(@"C:\\wl\\out\\__NAME__.rte", new SaveAsOptions { OverwriteExistingFile = true }); d.Close(false); Console.WriteLine("ROSETTA " + out_);
'''
GT=open(WL+'/jobs/geomdump.cs').read()
seed={2024:'ds0.rte',2026:'o26_line.rte'}[year]
guest.put(WL+'/files/'+{2024:'ds0.rte',2026:'o26_line.rte'}[year],'C:/wl/'+seed)
outdir=os.path.expanduser('~/rvt-research/rosetta'); os.makedirs(outdir,exist_ok=True); os.makedirs(os.path.expanduser('~/rvt-research/gt_geom'),exist_ok=True)
for name in only:
    desc,body=F[name]
    for v,lab in ((0,'base'),(1,'var')):
        if os.path.exists('%s/%d_%s_%s.rte'%(outdir,year,name,lab)) and os.path.exists(os.path.expanduser('~/rvt-research/gt_geom/%d_%s_%s.tsv'%(year,name,lab))): continue
        tag='ros_%s_%s'%(name,lab); fn='%d_%s_%s'%(year,name,lab)
        with guest.vmlock():
            port=guest.fresh(year)
            if not port: print(name,lab,'NO REVIT PORT, skipped',flush=True); continue
            if name in SEEDUP: guest.put(SEEDUP[name],'C:/wl/hb_%d.rte'%year); OVR[name]='C:\\wl\\hb_%d.rte'%year
            SEEDPATH=OVR.get(name) or 'C:\\wl\\'+seed
            cs=(PRE+body+POST).replace("__Y__",str(year)).replace('__SEEDPATH__',SEEDPATH).replace('__V__',str(v)).replace('__SEED__',seed).replace('__NAME__',tag)
            o=guest.run_job(year,port,cs,tag,400)
            ok='ROSETTA' in o
            print(name,lab,('created '+o[o.find('ROSETTA'):][:300].replace('\n',' ')) if ok else 'FAIL: '+o[:900].replace('\n',' '),flush=True)
            if not ok: continue
            guest.get('C:/wl/out/%s.rte'%tag,'%s/%s.rte'%(outdir,fn))
            gt=GT.replace('__FILE__','C:/wl/out/%s.rte'%tag).replace('__TAG__',tag+'_gt').replace('__START__','0').replace('__COUNT__','1000000').replace('__FAMMAX__','20')
            o2=guest.run_job(year,port,gt,tag+'_gt',600)
            if 'DONE' in o2: guest.get('C:/wl/out/%s_gt.gt'%tag,os.path.expanduser('~/rvt-research/gt_geom/%s.tsv'%fn)); print('  gt ok',flush=True)
            else: print('  gt FAIL',o2[-300:].replace('\n',' '),flush=True)
            guest.down(year)
