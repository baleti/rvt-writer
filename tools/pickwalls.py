#!/usr/bin/env python3
"""tools/pickwalls.py YEAR FILE.rte OUT.tsv : every wall/instance must be hit by a ReferenceIntersector ray (what 3D hover picks). env TOUCH=1 SAVE=guestpath SAVELOCAL=local"""
import sys,os,re; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,f,out=int(sys.argv[1]),os.path.abspath(sys.argv[2]),sys.argv[3]; base=os.path.basename(f); tag='pk_'+re.sub(r'\W','_',base)[:50]
cs=open(WL+'/jobs/pickwalls.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag).replace('__PHASE__',os.environ.get('PHASENAME','Phase 1')).replace('__TOUCH__',os.environ.get('TOUCH','0')).replace('__SAVE__',os.environ.get('SAVE',''))
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,900); print(o[-200:])
    guest.get('C:/wl/out/%s.pick'%tag,out)
    if os.environ.get('SAVE'): guest.get(os.environ['SAVE'],os.environ['SAVELOCAL'])
    guest.down(year)
r=open(out).read(); print([l for l in r.split('\n') if l.startswith(('PICK','CLS'))])
