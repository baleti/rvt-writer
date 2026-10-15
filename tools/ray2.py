#!/usr/bin/env python3
"""tools/ray2.py YEAR FILE OUT RAYS : jobs/ray2.cs (RAYS 'x,y,z,dx,dy;...')"""
import sys,os,re; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,f,out,rays=int(sys.argv[1]),os.path.abspath(sys.argv[2]),sys.argv[3],sys.argv[4]; base=os.path.basename(f); tag='r2_'+re.sub(r'\W','_',base)[:50]
cs=open(WL+'/jobs/ray2.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag).replace('__RAYS__',rays).replace('__TOUCH__',os.environ.get('TOUCH','0')).replace('__SAVE__',os.environ.get('SAVE',''))
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,900); print(o[-300:])
    guest.get('C:/wl/out/%s.ray'%tag,out)
    if os.environ.get('SAVE'): guest.get(os.environ['SAVE'],os.environ.get('SAVELOCAL','/tmp/claude-1000/touched.rte'))
    guest.down(year)
