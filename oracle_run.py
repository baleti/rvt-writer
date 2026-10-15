#!/usr/bin/env python3
"""oracle_run.py MODE YEAR FILE [OUTNAME] : run a ready-made Revit job from ~/src/rvt-sheets/oracle/ on FILE in the overlay VM.
MODE views  -> viewdump.cs  (__MAXIDS__=0)   -> ~/rvt-research/gt_views/<year>_<file>.views
MODE export -> viewexport.cs (__MAXVIEWS__=40 __PIXELS__=3000) -> ~/rvt-research/gt_views/<year>_<file>/ (png/dxf/pdf + index.tsv)
Compile errors are written to ~/rvt-research/gt_views/<tag>.err"""
import sys,os,re,zipfile; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
mode,year,f=sys.argv[1],int(sys.argv[2]),os.path.abspath(sys.argv[3]); base=os.path.basename(f); tag=('vd_' if mode=='views' else 've_')+re.sub(r'\W','_',base)[:60]
OUT=os.path.expanduser('~/rvt-research/gt_views'); os.makedirs(OUT,exist_ok=True)
REGEN=os.environ.get('REGEN')=='1'
src=open(os.path.expanduser('~/src/rvt-sheets/oracle/'+('viewdump.cs' if mode=='views' else 'viewexport.cs'))).read()
if REGEN: src=src.replace('new OpenOptions()); }','new OpenOptions()); using (var rt = new Transaction(d, "regen")) { rt.Start(); foreach (ViewPlan vp_ in new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().ToList()) { if (vp_.IsTemplate) continue; try { var dl = vp_.DetailLevel; vp_.DetailLevel = dl == ViewDetailLevel.Fine ? ViewDetailLevel.Medium : ViewDetailLevel.Fine; vp_.DetailLevel = dl; } catch { } } d.Regenerate(); rt.Commit(); } }',1)
cs=src.replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag).replace('__MAXIDS__','0').replace('__MAXVIEWS__','40').replace('__PIXELS__','3000')
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year)
    o=guest.run_job(year,p,cs,tag,2700); print(o[-800:])
    if 'ERROR' in o and '"kind": "compile"' in o:
        open('%s/%s.err'%(OUT,tag),'w').write(o); print('compile error written')
    elif mode=='views':
        guest.get('C:/wl/out/%s.views'%tag,'%s/%s.views'%(OUT,base if base.startswith(str(year)+'_') else '%d_%s'%(year,base))); print('wrote views')
    else:
        guest.script(r'Compress-Archive -Path "C:\wl\out\%s\*" -DestinationPath "C:\wl\out\%s.zip" -Force'%(tag,tag),300)
        z='/tmp/claude-1000/%s.zip'%tag; guest.get('C:/wl/out/%s.zip'%tag,z)
        nm=os.path.splitext(base)[0]; d='%s/%s'%(OUT,nm if nm.startswith(str(year)+'_') else '%d_%s'%(year,nm)); os.makedirs(d,exist_ok=True); zipfile.ZipFile(z).extractall(d); print('wrote',d)
    guest.down(year)
