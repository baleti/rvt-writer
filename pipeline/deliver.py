#!/usr/bin/env python3
"""deliver.py : copy every scene whose stageb_job log ends with PASS into scenes/<year>_writer_<name>.rte (+ report); print what was added"""
import os,re,shutil,glob
D=os.path.dirname(os.path.abspath(__file__)); WL=os.path.dirname(D); added=[]
for sh in sorted(glob.glob(D+'/done/*.sh')):
    s=open(sh).read(); m=re.search(r'stageb_job\.sh (\S+) (\d+) (\S+)',s); m2=re.search(r'full_job\.sh (\d+)',s)
    if m: name,year,f=m.group(1),m.group(2),m.group(3)
    elif m2: name,year,f='full',m2.group(1),'generated/full/full_%s.rte'%m2.group(1)     # full-coverage scene (pipeline/full_job.sh)
    else: continue
    lg=D+'/logs/'+os.path.basename(sh)+'.log'
    if not os.path.exists(lg): continue
    lines=[l.strip() for l in open(lg,errors='replace') if l.strip()]
    vc=[l for l in lines if l.startswith('VIEWCHECK')]
    if 'PASS' not in lines or any(l.startswith('FAIL') for l in lines) or (vc and not vc[-1].endswith('bad 0')): continue
    TESTS={'cols2','hosted2','text2','floors','params1','params2','sheets1','views1','types1','rooms1','open1','open2','open3','textA','vports1_2026','anno1_2026','spec_example_2026','grids1_2024','grids1','grids1r','shift1','vports1'}
    sub='classtests' if name in TESTS else ''
    src=os.path.join(WL,f); dst=os.path.join(WL,'scenes',sub,'%s_writer_%s.rte'%(year,name))
    if os.path.exists(src) and (not os.path.exists(dst) or open(src,'rb').read()!=open(dst,'rb').read()):
        shutil.copy(src,dst)
        if os.path.exists(src+'.report.json'): shutil.copy(src+'.report.json',dst.replace('.rte','.report.json'))
        added.append(os.path.basename(dst))
print('delivered',added)
