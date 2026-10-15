#!/usr/bin/env python3
"""verify_files.py MANIFEST.json OUT.tsv : full protocol for every file: fresh Revit per stage - API audit off, API audit on, UI (command line) path; SaveAs+reopen dump equality; dump vs generator manifest."""
import sys,os,json,time
WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign'); os.chdir(WL)
import stages,expect
man=json.load(open(sys.argv[1])); out=sys.argv[2]
only=sys.argv[3].split(',') if len(sys.argv)>3 else None
for m in man:
    if only and m['name'] not in only: continue
    if m['vcheck']!='PASS': open(out,'a').write('\t'.join([m['name'],str(m['year']),'offline FAIL','-','-','-','FAIL'])+'\n'); continue
    path=os.path.abspath(m['file']); res={}
    res['api']=stages.api_stage(m['year'],path,False,m['name']+'_a')
    res['audit']=stages.api_stage(m['year'],path,True,m['name']+'_b')
    res['ui']=stages.ui_stage(m['year'],path,m['name']+'_u')
    bad=[]
    if res['api'].get('ok'):
        dump=WL+'/campaign/work/%s_a_dump.txt'%m['name']; mf=path+'.json'
        if os.path.exists(dump) and os.path.exists(mf): bad=expect.check(dump,mf)
    ok=all(res[k].get('ok') for k in res) and not bad
    open(out,'a').write('\t'.join([m['name'],str(m['year']),'ok' if res['api'].get('ok') else 'FAIL:'+str(res['api'].get('err'))[:60],'ok' if res['audit'].get('ok') else 'FAIL:'+str(res['audit'].get('err'))[:60],
        'ok' if res['ui'].get('ok') else 'FAIL:'+str(res['ui'].get('err') or res['ui'].get('dialog'))[:60],'content:'+('ok' if not bad else ';'.join(bad[:3])),'PASS' if ok else 'FAIL'])+'\n')
    if ok:
        os.makedirs(WL+'/generated/clean',exist_ok=True)
        import shutil; shutil.copy(path,WL+'/generated/clean/'+os.path.basename(path)); shutil.copy(mf,WL+'/generated/clean/'+os.path.basename(path)+'.json')
