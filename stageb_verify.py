#!/usr/bin/env python3
"""stageb_verify.py YEAR FILE TAG MANIFEST : full protocol for a writer-built file. offline vcheck (caller), Revit API audit off/on (+SaveAs/reopen equal), UI open, Revit geometry export compared to the manifest."""
import sys,os,re,json,subprocess; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign'); os.environ['STAGEB']='1'
import stages
year=int(sys.argv[1]); f=os.path.abspath(sys.argv[2]); tag=sys.argv[3]; man=sys.argv[4]; res={}
for audit in (False,True):
    r=stages.api_stage(year,f,audit,tag+('a' if audit else 'n')); res['api_audit' if audit else 'api']=r
    print('API audit=%s ok=%s err=%s cmp=%s dialogs=%s failures=%s'%(audit,r['ok'],r.get('err'),r.get('cmp'),r.get('dialogs'),r.get('failures')),flush=True)
r=stages.ui_stage(year,f,tag+'u'); res['ui']=r; print('UI ok=%s docs=%s'%(r['ok'],r.get('docs')),flush=True)
rc=subprocess.run(['python3','-u',WL+'/geomexport.py',str(year),f,'--chunk','6000','--fam','3','--out',WL+'/generated/stageb/gt'],capture_output=True,text=True,timeout=1500)
print(rc.stdout[-300:],flush=True)
tsv=WL+'/generated/stageb/gt/%d_%s.tsv'%(year,os.path.basename(f))
c=subprocess.run(['python3',WL+'/stageb_check.py',tsv,man],capture_output=True,text=True); print(c.stdout[-1500:],flush=True); res['check']={'ok':c.returncode==0,'out':c.stdout[-800:]}
ok=all(v['ok'] for v in res.values())
json.dump({k:{kk:vv for kk,vv in v.items() if kk not in('journal','events')} for k,v in res.items()},open(WL+'/generated/stageb/%s.verify.json'%tag,'w'),indent=1,default=str)
print('PASS' if ok else 'FAIL')
