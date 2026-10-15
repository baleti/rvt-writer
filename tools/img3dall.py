#!/usr/bin/env python3
"""tools/img3dall.py YEAR OUTDIR FILE... : PNG + properties of EVERY existing 3D view of each file (the views the user opens) -> OUTDIR/<name>/ """
import sys,os,re,glob; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,outd=int(sys.argv[1]),sys.argv[2]
for f in sys.argv[3:]:
    f=os.path.abspath(f); base=os.path.basename(f); tag='ia_'+re.sub(r'\W','_',base)[:50]; od=os.path.join(outd,os.path.splitext(base)[0]); os.makedirs(od,exist_ok=True)
    cs=open(WL+'/jobs/img3dall.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag)
    with guest.vmlock():
        guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,900); print(base,o[-200:].replace('\n',' '))
        import shutil; shutil.rmtree(od+'/raw',ignore_errors=True); guest.get('C:/wl/out/%s'%tag,od+'/raw')
        guest.down(year)
