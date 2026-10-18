#!/usr/bin/env python3
"""tools/vg_scene.py YEAR NAME : build V/G oracle scene jobs/vg_NAME.cs on the seed house_base with the Revit API, then dump (viewdump rows + vgdump rows) and export PNG/DXF of its views.
Outputs: ~/rvt-research/vg-scenes/<year>_vg_NAME.rte, gt_views/<year>_vg_NAME.rte.views + .vg, gt_views/<year>_vg_NAME.rte/ (png/dxf/pdf + index.tsv)"""
import sys,os,re,subprocess; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,name=int(sys.argv[1]),sys.argv[2]; tag='vgs_%s_%d'%(name,year); R=os.path.expanduser('~/rvt-research'); EXT='.rvt' if name in ('worksets',) else '.rte'; out=R+'/vg-scenes/%d_vg_%s%s'%(year,name,EXT); os.makedirs(R+'/vg-scenes',exist_ok=True)
seed=os.environ.get('SEED') or R+'/rosetta/%d_house_base.rte'%year
PRE=open(WL+'/jobs/vg_prelude.cs').read()
VARIANT='1' if name.endswith('_var') else '0'; jobname=name[:-4] if name.endswith('_var') else name
cs=open(WL+'/jobs/vg_%s.cs'%jobname).read().replace('__VARIANT__',VARIANT).replace('//PRELUDE',PRE).replace('__SEED__','C:\\wl\\%s_seed.rte'%tag).replace('__OUT__','C:\\wl\\out\\%s%s'%(tag,EXT))
if not os.environ.get('SKIPBUILD'):
  with guest.vmlock():
    guest.put(seed,'C:/wl/%s_seed.rte'%tag); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,900); print(o[-700:]); open("/tmp/claude-1000/vgbuild_full.txt","w").write(o)
    if 'BUILT' not in o: sys.exit('build failed')
    guest.get('C:/wl/out/%s%s'%(tag,EXT),out); guest.down(year)
G=R+'/gt_views'; base=os.path.basename(out)
# viewdump + export through the shared oracle runner (own vmlock inside), then the extra rows
subprocess.run(['python3',WL+'/oracle_run.py','views',str(year),out],check=False)
ex=open(os.path.expanduser('~/src/rvt-sheets/oracle/viewexport.cs')).read()
ex=ex.replace('new OpenOptions()','new OpenOptions { DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets }')
k0=ex.index('var others ='); k1=ex.index('\n',k0)
ex=ex[:k0]+'var others = all.Where(v => !(v is ViewSheet) && v.Name.StartsWith("VG")).ToList(); sheets = new List<View>();'+ex[k1:]
t3=tag+'_ex'; ex=ex.replace('__FILE__','C:/wl/'+t3+EXT).replace('__TAG__',t3).replace('__MAXVIEWS__','99').replace('__PIXELS__','2400')
with guest.vmlock():
    guest.put(out,'C:/wl/%s%s'%(t3,EXT)); p=guest.fresh(year); o=guest.run_job(year,p,ex,t3,2400); print(o[-300:])
    import shutil; d=G+'/%d_vg_%s'%(year,name); shutil.rmtree(d,ignore_errors=True); guest.get('C:/wl/out/'+t3,d); guest.down(year)
vg=open(WL+'/jobs/vgdump.cs').read(); t2=tag+'_vg'
with guest.vmlock():
    guest.put(out,'C:/wl/%s%s'%(t2,EXT)); p=guest.fresh(year); o=guest.run_job(year,p,vg.replace('__FILE__','C:/wl/%s%s'%(t2,EXT)).replace('__TAG__',t2),t2,900); print(o[-500:])
    guest.get('C:/wl/out/%s.vg'%t2,'%s/%s.vg'%(G,base)); guest.down(year)
print('done',base)
