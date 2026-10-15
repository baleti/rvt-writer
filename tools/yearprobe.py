#!/usr/bin/env python3
"""yearprobe.py Y [Y..] : can Revit <year> start and expose the agent port in the guest? (holds vm.lock)"""
import sys,os,time; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
with guest.vmlock():
    for y in map(int,sys.argv[1:]):
        t=time.time()
        try: p=guest.fresh(y)
        except Exception as e: p=None; print(y,'EXC',e)
        print('YEAR',y,'port',p,'%.0fs'%(time.time()-t),flush=True)
        if p:
            o=guest.run_job(y,p,'Console.WriteLine("VER " + UIApp.Application.VersionNumber + " " + UIApp.Application.VersionBuild);','yp%d'%y,120); print('  ',o.strip()[-200:],flush=True)
        guest.down(y)
