#!/usr/bin/env python3
"""matexport.py YEAR FILE : Revit API material/appearance/layer/face-material export -> ~/rvt-research/gt_mat/<year>_<file>.tsv"""
import sys,os,re; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); f=os.path.abspath(sys.argv[2]); base=os.path.basename(f); tag='fma_'+re.sub(r'\W','_',base)
cs=open(WL+'/jobs/fmatall.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag)
os.makedirs(os.path.expanduser('~/rvt-research/gt_mat'),exist_ok=True)
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year)
    o=guest.run_job(year,p,cs,tag,2400); print(o[-600:])
    if 'DONE' in o: guest.get('C:/wl/out/%s.mat'%tag,os.path.expanduser('~/rvt-research/gt_mat/%d_%s.fmatall.tsv'%(year,os.path.splitext(base)[0]))); print('wrote')
    guest.down(year)
