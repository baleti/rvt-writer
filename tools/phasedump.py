#!/usr/bin/env python3
"""tools/phasedump.py YEAR FILE OUT.tsv : phases, phase filters, per-view phase settings, created/demolished phase + design option + workset counts per class"""
import sys,os,re; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,f,out=int(sys.argv[1]),os.path.abspath(sys.argv[2]),sys.argv[3]; base=os.path.basename(f); tag='ph_'+re.sub(r'\W','_',base)[:50]
cs=open(WL+'/jobs/phasedump.cs').read().replace('__FILE__','C:/wl/'+tag+'_'+base).replace('__TAG__',tag)
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_'+base); p=guest.fresh(year); o=guest.run_job(year,p,cs,tag,900); print(o[-200:]); guest.get('C:/wl/out/%s/phases.tsv'%tag,out); guest.down(year)
print(open(out).read())
