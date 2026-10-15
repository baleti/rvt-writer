#!/usr/bin/env python3
"""jobq: unattended sequential job runner. Drop an executable shell script into pipeline/queue/ (name sorts = order, e.g. 0100_cols_geom.sh;
first line comment '# timeout=SECONDS' optional). Runs one at a time, log -> pipeline/logs/<name>.log, moves to done/ or failed/ (rc!=0),
status -> pipeline/status.json, one-line result appended to LOG.md-style pipeline/RESULTS.tsv. Never exits."""
import os,time,json,subprocess,re,datetime
D=os.path.dirname(os.path.abspath(__file__)); Q=D+'/queue'
def mem_ok():
    except Exception: return 0
while True:
    jobs=sorted(f for f in os.listdir(Q) if f.endswith('.sh') and not f.startswith('.'))
    st={'time':datetime.datetime.now().isoformat(timespec='seconds'),'queued':jobs[:30],'running':None}
    if not jobs: json.dump(st,open(D+'/status.json','w'),indent=1); time.sleep(20); continue
    j=jobs[0]; p=Q+'/'+j; src=open(p).read(); m=re.search(r'#\s*timeout=(\d+)',src); to=int(m.group(1)) if m else 3600
    if '# vm' in src:
        w=0
        while mem_ok()<6000 and w<3600: time.sleep(120); w+=120
    st['running']=j; json.dump(st,open(D+'/status.json','w'),indent=1)
    t0=time.time(); log=open(D+'/logs/%s.log'%j,'w')
    try: rc=subprocess.run(['bash',p],stdout=log,stderr=subprocess.STDOUT,timeout=to,cwd=os.path.dirname(D)).returncode
    except subprocess.TimeoutExpired: rc=124; log.write('\nTIMEOUT after %ds\n'%to)
    log.close(); dst='done' if rc==0 else 'failed'
    try: os.rename(p,'%s/%s/%s'%(D,dst,j))
    except FileNotFoundError: pass
    open(D+'/RESULTS.tsv','a').write('%s\t%s\trc=%d\t%ds\t%s\n'%(datetime.datetime.now().strftime('%m-%d %H:%M'),j,rc,time.time()-t0,dst))
