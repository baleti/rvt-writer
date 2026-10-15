#!/usr/bin/env python3
"""tools/bis26t.py OUTDIR YEAR : one text note with lengths 1..12 (does pass/fail flip with byte size?)"""
import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import scenes
D=sys.argv[1]; Y=int(sys.argv[2])
for n in range(1,13):
    S=scenes.Scene('t%d'%n,Y); S.text(60,-6,'abcdefghijkl'[:n]); S.commit('%s/t%02d_%d.rte'%(D,n,Y))
    print(n,os.path.getsize('%s/t%02d_%d.rte'%(D,n,Y)))
