#!/usr/bin/env python3
"""tools/vg_scene.py YEAR NAME : build V/G oracle scene jobs/vg_NAME.cs on the seed house_base with the Revit API, then dump (viewdump rows + vgdump rows) and export PNG/DXF of its views.
Outputs: ~/rvt-research/vg-scenes/<year>_vg_NAME.rte, gt_views/<year>_vg_NAME.rte.views + .vg, gt_views/<year>_vg_NAME.rte/ (png/dxf/pdf + index.tsv)"""
import sys,os,re,subprocess; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,name=int(sys.argv[1]),sys.argv[2]; tag='vgs_%s_%d'%(name,year); R=os.path.expanduser('~/rvt-research'); out=R+'/vg-scenes/%d_vg_%s.rte'%(year,name); os.makedirs(R+'/vg-scenes',exist_ok=True)
seed=os.environ.get('SEED') or R+'/rosetta/%d_house_base.rte'%year
cs=open(WL+'/jobs/vg_%s.cs'%name).read().replace('__SEED__','C:\\wl\\%s_seed.rte'%tag).replace('__OUT__','C:\\wl\\out\\%s.rte'%tag)
if not os.environ.get('SKIPBUILD'):
  with guest.vmlock():
    guest.put(seed,'C:/wl/%s_seed.rte'%tag); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,900); print(o[-700:]); open("/tmp/claude-1000/vgbuild_full.txt","w").write(o)
    if 'BUILT' not in o: sys.exit('build failed')
    guest.get('C:/wl/out/%s.rte'%tag,out); guest.down(year)
G=R+'/gt_views'; base=os.path.basename(out)
# viewdump + export through the shared oracle runner (own vmlock inside), then the extra rows
subprocess.run(['python3',WL+'/oracle_run.py','views',str(year),out],check=False)
ex=open(os.path.expanduser('~/src/rvt-sheets/oracle/viewexport.cs')).read()
k0=ex.index('var others ='); k1=ex.index('\n',k0)
ex=ex[:k0]+'var others = all.Where(v => !(v is ViewSheet) && v.Name.StartsWith("VG")).ToList(); sheets = new List<View>();'+ex[k1:]
t3=tag+'_ex'; ex=ex.replace('__FILE__','C:/wl/'+t3+'.rte').replace('__TAG__',t3).replace('__MAXVIEWS__','99').replace('__PIXELS__','2400')
with guest.vmlock():
    guest.put(out,'C:/wl/%s.rte'%t3); p=guest.fresh(year); o=guest.run_job(year,p,ex,t3,2400); print(o[-300:])
    import shutil; d=G+'/%d_vg_%s'%(year,name); shutil.rmtree(d,ignore_errors=True); guest.get('C:/wl/out/'+t3,d); guest.down(year)
vg=open(WL+'/jobs/vgdump.cs').read(); t2=tag+'_vg'
with guest.vmlock():
    guest.put(out,'C:/wl/%s.rte'%t2); p=guest.fresh(year); o=guest.run_job(year,p,vg.replace('__FILE__','C:/wl/%s.rte'%t2).replace('__TAG__',t2),t2,900); print(o[-500:])
    guest.get('C:/wl/out/%s.vg'%t2,'%s/%s.vg'%(G,base)); guest.down(year)
print('done',base)
