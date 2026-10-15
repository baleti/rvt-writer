#!/usr/bin/env python3
"""viewexport.py YEAR FILE [--views id,id] [--els] : Revit API views/sheets/viewports/filters/overrides/templates -> ~/rvt-research/gt_views/<year>_<file>.tsv"""
import sys,os,re,argparse; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
ap=argparse.ArgumentParser(); ap.add_argument('year',type=int); ap.add_argument('file'); ap.add_argument('--views',default=''); ap.add_argument('--els',action='store_true'); ap.add_argument('--out',default=os.path.expanduser('~/rvt-research/gt_views'))
a=ap.parse_args(); f=os.path.abspath(a.file); base=os.path.basename(f); tag='view_'+re.sub(r'\W','_',base)
cs=open(WL+'/jobs/viewdump.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag).replace('__VIEWIDS__',a.views).replace('__ELIDS__','1' if a.els else '0')
os.makedirs(a.out,exist_ok=True)
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(a.year)
    o=guest.run_job(a.year,p,cs,tag,1800); print(o[-500:])
    if 'DONE' in o: guest.get('C:/wl/out/%s.view'%tag,'%s/%d_%s.tsv'%(a.out,a.year,base)); print('wrote')
    guest.down(a.year)
