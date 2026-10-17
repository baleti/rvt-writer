#!/usr/bin/env python3
"""tools/review_export.py YEAR FILE [OUTROOT] : Revit PNGs (3D incl. cameras.tsv, plans, section, elevation, sheets) -> OUTROOT/<name>/ (default ~/review-compare/revit). env PIXELS=2400 PLANS='L2,L5' NSHEETS=2"""
import sys,os,re,shutil; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,f=int(sys.argv[1]),os.path.abspath(sys.argv[2]); root=os.path.expanduser(sys.argv[3] if len(sys.argv)>3 else '~/review-compare/revit')
base=os.path.basename(f); name=os.path.splitext(base)[0]; tag='rv_'+re.sub(r'\W','_',base)[:50]; od=os.path.join(root,name)
cs=open(WL+'/jobs/reviewexport.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag).replace('__PIXELS__',os.environ.get('PIXELS','2400')).replace('__PLANS__',os.environ.get('PLANS','L2,Level 2,L1,Level 1')).replace('__NSHEETS__',os.environ.get('NSHEETS','2'))
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,1500); print(base,o[-300:].replace('\n',' '))
    shutil.rmtree(od,ignore_errors=True); guest.get('C:/wl/out/'+tag,od); guest.down(year)
