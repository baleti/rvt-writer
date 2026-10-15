#!/usr/bin/env python3
"""tools/img3d.py YEAR OUTDIR FILE... : fresh isometric 3D PNG of each file as Revit shows it -> OUTDIR/<name>.png"""
import sys,os,re,zipfile; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,outd=int(sys.argv[1]),sys.argv[2]; os.makedirs(outd,exist_ok=True)
for f in sys.argv[3:]:
    f=os.path.abspath(f); base=os.path.basename(f); tag='i3_'+re.sub(r'\W','_',base)[:50]
    cs=open(WL+'/jobs/img3d.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag)
    with guest.vmlock():
        guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,900); print(base,o[-200:].replace('\n',' '))
        guest.get('C:/wl/out/%s/iso.png'%tag,'%s/%s.png'%(outd,os.path.splitext(base)[0])); guest.down(year)
