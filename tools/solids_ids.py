#!/usr/bin/env python3
"""tools/solids_ids.py YEAR FILE ID,ID,... OUT.tsv : per-element Revit solids (Medium + Fine detail, instance+symbol geometry) and Volume/Area params, overlay VM."""
import sys,os,re; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,f,ids,out=int(sys.argv[1]),os.path.abspath(sys.argv[2]),sys.argv[3],sys.argv[4]; base=os.path.basename(f); tag='sol_'+re.sub(r'\W','_',base)[:50]
cs=open(WL+'/jobs/solids_ids.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag).replace('__IDS__',ids)
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,1800); print(o[-400:])
    guest.get('C:/wl/out/%s.tsv'%tag,out); guest.down(year)
