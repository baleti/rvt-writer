#!/usr/bin/env python3
"""regen2020.py - the 2020 edit deliverables rebuilt with the current writer (stamps recomputed): same-size rename, length-changing renames, numeric edit, parameter add, delete."""
import sys,os,json,struct,subprocess; os.chdir(os.path.expanduser('~/rvt-research/write-lab')); sys.path.insert(0,'.')
import rvtgen
SEED='files/orig2020.rvt'; OUT='generated/new/'
def run(name,fn,manifest):
    g=rvtgen.Gen(SEED); fn(g); out=OUT+name+'.rvt'; g.commit(out); json.dump(manifest,open(out+'.json','w')); print(name,'built')
    r=subprocess.run(['python3','vcheck.py',out,'--seed',SEED,'--manifest',out+'.json'],capture_output=True,text=True); print('  vcheck',r.stdout.strip().splitlines()[-1],[l for l in r.stdout.splitlines() if l.startswith('FAIL')][:3])
    return dict(name=name,file=out,year=2020,vcheck='PASS' if r.returncode==0 else 'FAIL',detail=[l for l in r.stdout.splitlines() if l.startswith('FAIL')][:3])
def ren(eid,field,newname,match=None):
    def f(g):
        pn,i,r,log,q=g.e.trace(eid); g.edits=getattr(g,'edits',[])+[(i,lambda: g.e.set_string(eid,field,newname,match=match))]
    return f
def multi(*fs):
    def f(g):
        for x in fs: x(g)
    return f
def numeric(g):
    pn,i,r,log,q=g.e.trace(1351691)
    def do():
        b=g.e.m.parts[pn]['joined']; eds=[]
        for l in log:
            if l[1]=='Plane.m_origin': x,y,_=struct.unpack_from('<3d',b,l[2]); eds.append((l[2],24,struct.pack('<3d',x,y,-9.84251968503937)))
            if l[1]=='Level.m_isBuildingStory': eds.append((l[2],1,bytes([1-b[l[2]]])))
        g.e.modify(1351691,eds)
    g.edits=getattr(g,'edits',[])+[(i,do)]
def addparam(g):
    pn,i,r,log,q=g.e.trace(857191)
    def do():
        st=[l for l in log if l[1]=='ParamValueSetAString.m_paramSet'][0][2]; txt='Added by write-lab'
        b=txt.encode('utf-16le'); entry=struct.pack('<I',(-1010106)&0xffffffff)+struct.pack('<I',len(b)//2)+b
        g.e.modify(857191,[(st,4,struct.pack('<I',3)),(st+4,0,entry)])
    g.edits=getattr(g,'edits',[])+[(i,do)]
def delete(g): g.delete(1386050)
M=[]
M.append(run('e1_level_rename_same_2020',ren(1351691,'DatumPlane.m_text','FOUNDATION-EDIT'),{'renames':[[1351691,'FOUNDATION-EDIT']]}))
M.append(run('e3_level_rename_long_2020',ren(1351691,'DatumPlane.m_text','FOUNDATION-2700-EXTENDED-NAME é楔'),{'renames':[[1351691,'FOUNDATION-2700-EXTENDED-NAME é楔']]}))
M.append(run('e2_level_elevation_2020',numeric,{'edited':[1351691]}))
M.append(run('e5_room_param_2020',addparam,{'edited':[857191]}))
M.append(run('e6_delete_textnote_2020',delete,{'deleted':[1386050]}))
json.dump(M,open(OUT+'MANIFEST2020.json','w'),indent=1)
