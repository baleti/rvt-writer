#!/usr/bin/env python3
"""regen_all.py - rebuild every deliverable with the current writer into generated/new/ and run the offline checker; writes generated/new/MANIFEST.json"""
import sys,os,json,subprocess
WL=os.path.expanduser('~/rvt-research/write-lab'); os.chdir(WL)
def mk(name,spec):
    spec['name']=name; f='generated/new/%s.spec.json'%name; json.dump(spec,open(f,'w')); out='generated/new/%s.rte'%name
    r=subprocess.run(['python3','campaign/make.py',f,out],capture_output=True,text=True); return out,r.returncode==0,r.stdout[-200:]+r.stderr[-300:]
S=[]
for y in (2024,2026):
    S+=[('koch2_%d'%y,{'seed':1,'year':y,'parts':[{'op':'lines','shape':'koch','level':355,'depth':2,'size':120,'cx':-60,'cy':-30}]}),
        ('koch3_%d'%y,{'seed':1,'year':y,'parts':[{'op':'lines','shape':'koch','level':355,'depth':3,'size':120,'cx':-60,'cy':-30}]}),
        ('koch4_%d'%y,{'seed':1,'year':y,'parts':[{'op':'lines','shape':'koch','level':355,'depth':4,'size':120,'cx':-60,'cy':-30}]}),
        ('sier4_%d'%y,{'seed':1,'year':y,'parts':[{'op':'lines','shape':'sier','level':355,'depth':4,'size':120,'cx':-60,'cy':-30}]}),
        ('spiral150_%d'%y,{'seed':1,'year':y,'parts':[{'op':'lines','shape':'spiral','level':355,'n':150,'size':120}]}),
        ('star90_%d'%y,{'seed':1,'year':y,'parts':[{'op':'lines','shape':'star','level':355,'n':90,'size':120}]}),
        ('tower30_waist_%d'%y,{'seed':1,'year':y,'parts':[{'op':'tower','levels':30,'spacing':'golden','step':13,'start':40,'sides':8,'r0':45,'law':'waist','twist':4.5,'prefix':'T'}]}),
        ('tower20_taper_hex_%d'%y,{'seed':1,'year':y,'parts':[{'op':'tower','levels':20,'spacing':'linear','step':13.5,'start':40,'sides':6,'r0':40,'law':'taper','twist':3,'prefix':'T'}]}),
        ('tower24_bulge_pent_%d'%y,{'seed':7,'year':y,'parts':[{'op':'tower','levels':24,'spacing':'sine','step':12,'start':40,'sides':5,'r0':40,'law':'bulge','twist':-6,'prefix':'T'}]}),
        ('levels30_golden_%d'%y,{'seed':1,'year':y,'parts':[{'op':'levels','n':30,'spacing':'golden','step':14,'start':40,'prefix':'L'}]}),
        ('walls_ring_%d'%y,{'seed':1,'year':y,'parts':[{'op':'walls','level':355,'shape':'poly','n':8,'size':40,'h':14,'hlaw':'saw'}]}),
        ('walls_fan_lines_%d'%y,{'seed':2,'year':y,'parts':[{'op':'walls','level':2607,'shape':'fan','n':24,'size':35,'h':10,'hlaw':'sine'},{'op':'lines','level':355,'shape':'koch','depth':2,'size':60,'cx':80}]}),
        ('fills_%d'%y,{'seed':1,'year':y,'parts':[{'op':'fills','n':10,'prefix':'WLP'}]}),
        ('rename_short_%d'%y,{'seed':1,'year':y,'parts':[{'op':'rename_level','id':5877,'name':'T.O. EDIT'}]}),
        ('rename_long_%d'%y,{'seed':1,'year':y,'parts':[{'op':'rename_level','id':5877,'name':'T.O. Slab - renamed to a much longer level name é楔'}]})]
man=[]
for name,spec in S:
    out,ok,msg=mk(name,spec); print(name,'OK' if ok else 'MAKEFAIL '+msg[-200:])
    if not ok: continue
    seed={2024:'files/ds0.rte',2026:'files/o26_line.rte'}[spec['year']]
    r=subprocess.run(['python3','vcheck.py',out,'--seed',seed,'--manifest',out+'.json'],capture_output=True,text=True)
    man.append(dict(name=name,file=out,year=spec['year'],vcheck=('PASS' if r.returncode==0 else 'FAIL'),detail=[l for l in r.stdout.splitlines() if l.startswith('FAIL')][:3]))
    print('   vcheck',man[-1]['vcheck'],man[-1]['detail'])
json.dump(man,open('generated/new/MANIFEST.json','w'),indent=1)
