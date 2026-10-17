#!/usr/bin/env python3
"""tools/fam_save.py YEAR PROJECT.rvt OUTDIR : EditFamily + SaveAs of every editable family of PROJECT (opened in Revit YEAR; older files are upgraded in memory) -> OUTDIR/<Category>/<Family>.rfa (+ compact/), index.tsv. Chunks of 15 families per Revit call."""
import sys,os,re,shutil; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,f,od=int(sys.argv[1]),os.path.abspath(sys.argv[2]),os.path.expanduser(sys.argv[3]); base=os.path.basename(f); tag='fs_'+re.sub(r'\W','_',base)[:40]; CH=int(os.environ.get('CHUNK','15'))
src=open(WL+'/jobs/famsave.cs').read(); os.makedirs(od,exist_ok=True)
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'.rvt'); p=guest.fresh(year); start=0; total=None
    while True:
        cs=src.replace('__FILE__','C:/wl/'+tag+'.rvt').replace('__TAG__',tag).replace('__START__',str(start)).replace('__COUNT__',str(CH))
        o=guest.run_job(year,p,cs,tag+'_%d'%start,1200); m=re.search(r'DONE total=(\d+) did=(\d+)',o); print(start,o[-200:].replace('\n',' '),flush=True)
        if not m: break
        total=int(m.group(1)); start+=CH
        if start>=total: break
    guest.get('C:/wl/out/'+tag,od+'/_raw'); guest.down(year)
# merge
raw=od+'/_raw'
if os.path.isdir(raw):
    with open(od+'/index.tsv','w') as out:
        for fn in sorted(x for x in os.listdir(raw) if x.startswith('index_')):
            out.write(open(raw+'/'+fn).read())
    for d_ in os.listdir(raw):
        if os.path.isdir(raw+'/'+d_):
            shutil.copytree(raw+'/'+d_,od+'/'+d_,dirs_exist_ok=True)
    shutil.rmtree(raw)
print('done',od)
