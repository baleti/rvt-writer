#!/usr/bin/env python3
"""tools/latest_diff.py YEAR ROSETTA_BASE ROSETTA_VAR : list the byte-level differences of Global/Latest between two rosettas (opcodes of a SequenceMatcher on 64-byte blocks aligned by hash)"""
import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,difflib
def latest(path):
    g=rvtgen.Gen(os.path.expanduser(path)); cap={}
    def f(raw): cap['r']=bytes(raw); return raw
    g.e.global_edit('Global/Latest',f); return cap['r']
b=latest(sys.argv[1]); v=latest(sys.argv[2]); print(len(b),len(v))
sm=difflib.SequenceMatcher(None,b,v,autojunk=False)
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag!='equal': print(tag,i1,i2,j1,j2,b[i1:i2][:48].hex(),'->',v[j1:j2][:48].hex(),len(v[j1:j2]))
