#!/usr/bin/env python3
"""tools/review_pdf.py YEAR FILE IDS OUTDIR : Revit PDF (one per view/sheet id, comma list) of FILE opened in the Revit YEAR of the VM (older files are upgraded in memory) -> OUTDIR/<id>.pdf"""
import sys,os,re; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,f,ids,od=int(sys.argv[1]),os.path.abspath(sys.argv[2]),sys.argv[3],os.path.expanduser(sys.argv[4]); base=os.path.basename(f); tag='rp_'+re.sub(r'\W','_',base)[:40]
cs=open(WL+'/jobs/reviewpdf.cs').read().replace('__FILE__','C:/wl/'+tag+'.rvt').replace('__TAG__',tag).replace('__IDS__',ids)
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'.rvt'); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,1500); print(o[-400:])
    os.makedirs(od,exist_ok=True); guest.get('C:/wl/out/'+tag,od+'/_raw'); guest.down(year)
