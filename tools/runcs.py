#!/usr/bin/env python3
"""tools/runcs.py YEAR JOB.cs IN.rte OUT_LOCAL.rte [GUEST_OUT_NAME]: run a job (placeholders __FILE__ input guest path, __OUT__ output guest path) on IN, fetch the saved file"""
import sys,os,re; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year,cs,f,out=int(sys.argv[1]),sys.argv[2],os.path.abspath(sys.argv[3]),sys.argv[4]; tag='rc_'+re.sub(r'\W','_',os.path.basename(cs))[:30]
src=open(cs).read().replace('__FILE__','C:\\wl\\'+tag+'_in.rte').replace('__OUT__','C:\\wl\\out\\'+tag+'_out.rte')
with guest.vmlock():
    guest.put(f,'C:/wl/'+tag+'_in.rte'); p=guest.fresh(year); o=guest.run_job(year,p,src,tag,900); print(o[-600:]); open(out+'.log','w').write(o)
    guest.get('C:/wl/out/'+tag+'_out.rte',out); guest.down(year)
