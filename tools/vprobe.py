#!/usr/bin/env python3
"""tools/doordump.py YEAR FILE OUT [VIEWIDS] : jobs/vprobe.cs on FILE in the overlay VM -> OUT (DOOR / INVIEW rows)"""
import sys,os,re; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,f,out=int(sys.argv[1]),os.path.abspath(sys.argv[2]),sys.argv[3]; views=sys.argv[4] if len(sys.argv)>4 else ''
base=os.path.basename(f); tag="vp_"+re.sub(r'\W','_',base)[:60]
cs=open(WL+'/jobs/vprobe.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag).replace('__VIEW__',views)
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year)
    o=guest.run_job(year,p,cs,tag,1200); print(o[-800:])
    guest.get('C:/wl/out/%s.doors'%tag,out); print('wrote',out)
    guest.down(year)
