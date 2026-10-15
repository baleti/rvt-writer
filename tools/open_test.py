#!/usr/bin/env python3
"""open_test.py YEAR FILE TAG : Revit API open (audit off) + UI-free result summary"""
import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign'); os.environ['STAGEB']='1'
import stages
r=stages.api_stage(int(sys.argv[1]),os.path.abspath(sys.argv[2]),False,sys.argv[3]); print('OPEN ok=%s err=%s'%(r['ok'],r.get('err')))
