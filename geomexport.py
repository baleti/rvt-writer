#!/usr/bin/env python3
"""geomexport.py YEAR FILE [--chunk N] [--fam N] : run jobs/geomdump.cs in Revit (my overlay VM) in chunks, merge into ~/rvt-research/gt_geom/<year>_<file>.tsv"""
import sys,os,re,time,argparse
sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab/campaign'))
import guest
WL=os.path.expanduser('~/rvt-research/write-lab')
ap=argparse.ArgumentParser(); ap.add_argument('year',type=int); ap.add_argument('file'); ap.add_argument('--chunk',type=int,default=400); ap.add_argument('--fam',type=int,default=30); ap.add_argument('--out',default=os.path.expanduser('~/rvt-research/gt_geom'))
a=ap.parse_args()
TPL=open(WL+'/jobs/geomdump.cs').read(); base=os.path.basename(a.file); tag='gt_'+re.sub(r'\W','_',base)
guest.put(os.path.abspath(a.file),'C:/wl/'+tag+'_'+base)
PORT=[None]
def job(start,count,fam,fresh=False):
    if fresh or not PORT[0]: PORT[0]=guest.fresh(a.year)
    return _job(start,count,fam)
def _job(start,count,fam):
    cs=TPL.replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag).replace('__START__',str(start)).replace('__COUNT__',str(count)).replace('__FAMMAX__',str(fam))
    if not PORT[0]: return None
    return guest.run_job(a.year,PORT[0],cs,tag,1200)
_lk=guest.vmlock(); _lk.__enter__()
out=job(0,0,0); m=re.search(r'DONE (\d+)',out or ''); 
if not m: print('count job failed:',(out or '')[-400:]); sys.exit(1)
total=int(m.group(1)); print('elements',total)
os.makedirs(a.out,exist_ok=True); dst='%s/%d_%s.tsv'%(a.out,a.year,base); open(dst,'w').close()
start=0; chunk=a.chunk
while start<total:
    t0=time.time(); o=job(start,chunk,a.fam if start+chunk>=total or start==0 else a.fam)
    ok=o and 'DONE' in o
    if not ok:
        PORT[0]=None
        if chunk>20: chunk//=4; print('chunk failed, shrinking to',chunk); continue
        print('element chunk at',start,'failed even at',chunk); start+=chunk; continue
    guest.get('C:/wl/out/%s.gt'%tag,WL+'/campaign/work/%s.part'%tag)
    open(dst,'ab').write(open(WL+'/campaign/work/%s.part'%tag,'rb').read())
    print('chunk',start,'-',start+chunk,'ok',round(time.time()-t0),'s'); start+=chunk
guest.down(a.year); _lk.__exit__(); print('wrote',dst,os.path.getsize(dst))
