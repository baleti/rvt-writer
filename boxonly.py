#!/usr/bin/env python3
"""boxonly.py YEAR FILE IDSFILE OUT : geometry presence per element id (jobs/boxonly.cs)"""
import sys,os,re; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); f=os.path.abspath(sys.argv[2]); ids=','.join(re.findall(r'\d+',open(sys.argv[3]).read())); out=sys.argv[4]; base=os.path.basename(f); tag='bx_'+re.sub(r'\W','_',base)
cs=open(WL+'/jobs/boxonly.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag).replace('__IDS__',ids)
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year)
    o=guest.run_job(year,p,cs,tag,1500); print(o[-600:])
    if 'DONE' in o: guest.get('C:/wl/out/%s.boxonly'%tag,out); print('wrote',out)
    guest.down(year)
