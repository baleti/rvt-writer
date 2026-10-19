"""genlib2: Stage B element makers cloned from Revit-saved seeds (FamilyInstance columns first)."""
import struct,math,sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import genlib
from genlib import rep,restamp,hdr_ids,_row,setphase
def make_column(g,T,nid,x,y,z=0.0,level_id=None):
    """T = template() of a Revit-made structural column FamilyInstance (house_base 301563: UC305x305x97 at (2,2,0) on Level 355).
    Patched: id, instOrigin, Trf.m_or, header outline (bbox shifts with the origin), item (zone record) x,y copies; same type/level/symbol copy as the template."""
    W=8; L={n:(o,e) for n,o,e,_ in T['log']}; idb=nid.to_bytes(W,'little')
    rec=bytearray(T['rec']); rec[4:12]=idb; rec[L['Element.m_id'][0]:L['Element.m_id'][1]]=idb
    ox,oy,oz=struct.unpack_from('<3d',rec,L['FamilyInstance.m_instOrigin'][0])
    struct.pack_into('<3d',rec,L['FamilyInstance.m_instOrigin'][0],x,y,z)
    tox,toy,toz=struct.unpack_from('<3d',rec,L['Trf.m_or'][0]); struct.pack_into('<3d',rec,L['Trf.m_or'][0],x+(tox-ox),y+(toy-oy),z+(toz-oz))
    if level_id is not None: struct.pack_into('<Q',rec,L['Element.m_assocLevelId'][0],level_id)
    hdr,hl=hdr_ids(T,nid,W)
    a=hl['Outline.m_minmax'][0]; o=list(struct.unpack_from('<6d',hdr,a)); dx,dy,dz=x-ox,y-oy,z-oz
    struct.pack_into('<6d',hdr,a,o[0]+dx,o[1]+dy,o[2]+dz,o[3]+dx,o[4]+dy,o[5]+dz)
    item=bytearray(T['item']); rep(item,T['tid'].to_bytes(W,'little'),idb)
    for px,py in ((272,280),(344,352),(428,436),(548,556)):
        ix=struct.unpack_from('<d',item,px)[0]; iy=struct.unpack_from('<d',item,py)[0]
        struct.pack_into('<d',item,px,ix+dx); struct.pack_into('<d',item,py,iy+dy)
    rec=bytearray(g.stamp(bytes(rec))); setphase(hdr); setphase(rec); rec=g.stamp(bytes(rec)); setphase(item); item=restamp(bytes(item),W)
    return bytes(hdr),rec,bytes(item)

def make_hosted_x(g,T,nid,x,item_x_off=None,idmap=None):
    """clone a hosted FamilyInstance (door/window) of a Revit-made template, moved along x only (host wall along +x, same host, same type/sill).
    patched: id, m_hostParam, m_instOrigin.x, Trf.m_or.x, header outline x, item x copy"""
    W=8; L={n:(o,e) for n,o,e,_ in T['log']}; idb=nid.to_bytes(W,'little')
    rec=bytearray(T['rec']); rec[4:12]=idb; rec[L['Element.m_id'][0]:L['Element.m_id'][1]]=idb
    if idmap: rec=bytearray(rep_many(rec,idmap))
    ox=struct.unpack_from('<3d',rec,L['FamilyInstance.m_instOrigin'][0])[0]; dx=x-ox
    if item_x_off is None:
        cand=[o for o in range(0,len(T['item'])-7) if struct.unpack_from('<d',T['item'],o)[0]==ox and ox!=0.0]
        item_x_off=cand[0] if len(cand)==1 else 276
    for nm,idx in (('FamilyInstance.m_instOrigin',0),('Trf.m_or',0)):
        o=L[nm][0]+8*idx; struct.pack_into('<d',rec,o,struct.unpack_from('<d',rec,o)[0]+dx)
    o=L['InsertableInst.m_hostParam'][0]; struct.pack_into('<d',rec,o,struct.unpack_from('<d',rec,o)[0]+dx)
    hdr,hl=hdr_ids(T,nid,W); a=hl['Outline.m_minmax'][0]; v=list(struct.unpack_from('<6d',hdr,a)); v[0]+=dx; v[3]+=dx; struct.pack_into('<6d',hdr,a,*v)
    if idmap: hdr=bytearray(rep_many(hdr,idmap))
    item=bytearray(T['item']); rep(item,T['tid'].to_bytes(W,'little'),idb)
    if idmap: item=bytearray(rep_many(item,idmap))
    struct.pack_into('<d',item,item_x_off,struct.unpack_from('<d',item,item_x_off)[0]+dx)
    # the item also caches the instance outline (2 copies of min/max): move its x like the header outline. Without this Revit kept
    # every copy's bounding box at the template's position (house1 doors all at x 8.25..11.75; found 2026-10-15)
    h0,_=hdr_ids(T,T['tid'],W); a0=_['Outline.m_minmax'][0]; ov=struct.unpack_from('<6d',h0,a0); xs={ov[0],ov[3]}
    for o in range(0,len(item)-7):
        if o!=item_x_off and struct.unpack_from('<d',T['item'],o)[0] in xs: struct.pack_into('<d',item,o,struct.unpack_from('<d',T['item'],o)[0]+dx)
    rec=bytearray(g.stamp(bytes(rec))); setphase(hdr); setphase(rec); rec=g.stamp(bytes(rec)); setphase(item); item=restamp(bytes(item),W)
    return bytes(hdr),rec,bytes(item)

def make_textnote(g,T,nid,x,y,text,width_per_char=0.121751968503937/18,z=0.0):
    """clone a Revit-made TextNote (house_base 301590) with new id, position and text (BMP chars; rich-text stream rewritten)."""
    W=8; L={n:(o,e) for n,o,e,_ in T['log']}; idb=nid.to_bytes(W,'little'); r=bytes(T['rec'])
    f0,f1=L['TextElement.m_arrTextFragments']; rt0,rt1=L['RtfData.m_arrRtfStream']
    old=r[f0:f1]; assert struct.unpack_from('<I',old,0)[0]==1
    n=len(text); u=text.encode('utf-16-le')
    frag=struct.pack('<I',1)+struct.pack('<I',n)+u+struct.pack('<I',n)+old[len(old)-12:]        # count, len, utf16, nLengthInRichEditCtrl, mask/effects/numbering
    rtf=r[rt0+4:rt1]; i=rtf.index(b'\\fs24 ')+6; j=rtf.index(b'\\par',i)
    rtf=rtf[:i]+text.encode('cp1252',errors='replace').replace(b'\\',b'\\\\')+rtf[j:]
    body=r[:f0]+frag+r[f1:rt0]+struct.pack('<I',len(rtf))+rtf+r[rt1:]
    rec=bytearray(body); dfrag=len(frag)-(f1-f0)
    def sh(nm): return L[nm][0]+(dfrag if L[nm][0]>=f1 else 0)       # fields between the fragment and the rtf stream only shift by the fragment growth
    rec[4:12]=idb; rec[L['Element.m_id'][0]:L['Element.m_id'][1]]=idb
    struct.pack_into('<3d',rec,sh('TextElement.m_orig'),x,y,z)
    w=width_per_char*n
    for nm in ('TextElement.m_lineWidth','TextElement.m_maxWidth','TextElement.m_trueWidth'): struct.pack_into('<d',rec,sh(nm),w)
    hdr=bytearray(T['hdr']); hdr[0:W]=idb
    hl={a:(b,c) for a,b,c,_ in T['hlog']}
    item=bytearray(T['item']); rep(item,T['tid'].to_bytes(W,'little'),idb)
    rec=bytearray(g.stamp(bytes(rec))); setphase(hdr); setphase(rec); rec=g.stamp(bytes(rec)); setphase(item); item=restamp(bytes(item),W)
    return bytes(hdr),bytes(rec),bytes(item)

def registry_ops(raw,tid,new_ids,must=None):
    """Global/Latest keeps id lists per category/class ([count u32][ids u64..]); for every list that STARTS with the template element's id,
    append the new ids and bump the count. returns ops (pos,delete_len,insert_bytes) as used by Builder.commit"""
    ops=[]; idb=struct.pack('<Q',tid); k=-1
    while True:
        k=raw.find(idb,k+1)
        if k<0: break
        if k<4: continue
        n=struct.unpack_from('<I',raw,k-4)[0]
        if not 1<=n<20000 or k+8*n>len(raw): continue
        ids=struct.unpack_from('<%dQ'%n,raw,k)
        if any(i>=1<<40 for i in ids) or list(ids)!=sorted(ids): continue
        if must is not None and must not in ids: continue
        if must is None and False: continue
        ops.append((k-4,4+8*n,struct.pack('<I',n+len(new_ids))+raw[k:k+8*n]+b''.join(struct.pack('<Q',i) for i in new_ids)))
    return ops

# ---------------- rectangular floors (7 linked elements + 1 span-direction line): fitted from rosetta/2024_floors12_base (landscape W>=D) -------------
import json as _json
YEAR=2024
_FF={}
def _suf(): return '' if YEAR==2024 else '_%d'%YEAR
def _floorfit():
    if YEAR not in _FF: _FF[YEAR]=_json.load(open(os.path.expanduser('~/rvt-research/write-lab/files/floorfit%s.json'%_suf())))
    return _FF[YEAR]
def _ffeats(x0,y0,W,D):
    return {'1':1.0,'x0':x0,'y0':y0,'W':W,'D':D,'x1':x0+W,'y1':y0+D,'xm':x0+W/2,'ym':y0+D/2,'WD':W*D,'W2D2':2*(W+D),'hW':W/2,'hD':D/2,'D13':D/3,'D23':2*D/3,'xsd':x0+W/2-D/3,'nD13':-D/3}
FLOOR_ROLES=['sp','vs','fl','c0','c1','c2','c3','c4']
class FloorTpl:
    """templates of the 8 elements of one Revit floor from a floors12 file (group 0 = rect (0,0,40,26))"""
    def __init__(self,gen,ids8):
        self.T={r:gen.template(i) for r,i in zip(FLOOR_ROLES,ids8)}; self.ids=ids8
def make_floor(g,FT,nids,x0,y0,W,D,z=0.0,level_id=355):
    """nids: 8 new ids in role order. returns list of (hdr,rec,item,nid,row_template_role)"""
    pass  # any W,D (portrait checked 2026-10-17)
    ft=_ffeats(x0,y0,W,D); fit=_floorfit(); out=[]; idmap={FT.ids[i]:nids[i] for i in range(8)}; idmap[355]=level_id
    slope=_json.load(open(os.path.expanduser('~/rvt-research/write-lab/files/floorslope%s.json'%_suf())))
    for r,nid in zip(FLOOR_ROLES,nids):
        T=FT.T[r]; parts={}
        for key in ('rec','hdr','item'):
            b=bytearray(T[key])
            b=bytearray(rep_many(b,idmap))
            fd=fit.get(r+'.'+key,{}).get('found',{})
            for off,(fn,co) in fd.items():
                struct.pack_into('<d',b,int(off),sum(c*ft[f] for f,c in zip(fn,co)))
            for off,sl in slope.get(r+'.'+key,{}).items():
                if z: struct.pack_into('<d',b,int(off),struct.unpack_from('<d',b,int(off))[0]+sl*z)
            parts[key]=b
        rec=bytearray(g.stamp(bytes(parts['rec']))); hdr=parts['hdr']; item=parts['item']
        if r=='fl':      # Revit's spatial pick key of the slab (item[172], same loose-octree key as walls; strict at 0): a stale key makes the floor unpickable in 3D
            hl={x[0]:x for x in T['hlog']}; item[172:176]=genlib.spatial_key(struct.unpack_from('<6d',hdr,hl['Outline.m_minmax'][1]),False)
        setphase(hdr); setphase(rec); rec=g.stamp(bytes(rec)); setphase(item); item=restamp(bytes(item),8)
        row=bytearray(T['row']); row[0:8]=nid.to_bytes(8,'little'); row[20:28]=nid.to_bytes(8,'little')
        out.append((bytes(hdr),bytes(rec),bytes(item),nid,bytes(row)))
    return out

def registry_update(raw,groups,known):
    """groups: {template_id: [new ids appended to every Latest id-list that contains template_id]}; lists are [count u32][ids u64 ascending], all ids must be known element ids.
    returns non-overlapping ops (pos,delete_len,insert_bytes)"""
    lists={}   # start -> n
    for tid in groups:
        b=struct.pack('<Q',tid); k=-1
        while True:
            k=raw.find(b,k+1)
            if k<0: break
            for j in range(0,400):
                s=k-8*j
                if s<4: break
                n=struct.unpack_from('<I',raw,s-4)[0]
                if n<j+1 or n>20000 or s+8*n>len(raw): continue
                ids=struct.unpack_from('<%dQ'%n,raw,s)
                if list(ids)==sorted(ids) and all(i in known for i in ids): lists[s]=(n,ids); break
    ops=[]
    for s,(n,ids) in lists.items():
        add=[]
        for tid,new in groups.items():
            if tid in ids: add+=new
        add=sorted(set(add))
        if add: ops.append((s-4,4+8*n,struct.pack('<I',n+len(add))+raw[s:s+8*n]+b''.join(struct.pack('<Q',i) for i in add)))
    return ops
def apply_ops(raw,ops):
    out=bytearray(raw)
    for pos,dl,ins in sorted(ops,key=lambda o:-o[0]): out[pos:pos+dl]=ins
    return bytes(out)


def level_offsets(raw,year=2024,ref=None):
    ref=ref or os.path.expanduser('~/rvt-research/write-lab/files/'+{2024:'ds0.rte',2026:'o26_line.rte'}[year])
    """offsets of the 8 Level-registry anchors in this file's Global/Latest, found by the 24 bytes of context they have in the ds0 seed"""
    import adiff
    from gen_levels import LATEST_OFFS
    a=adiff.graw(ref,'Global/Latest'); out=[]
    for o in LATEST_OFFS[year]:
        ctx=a[o-24:o+8]; k=raw.find(ctx); assert k>=0 and raw.find(ctx,k+1)<0,('level anchor not unique',o); out.append(k+24)
    return tuple(out)
def make_level(g,TL,nid,name,z,tr):
    return genlib.make_level(g,TL,nid,name,z,tr)

# ---------------- generic fitted FamilyInstance maker (columns/windows/doors with levels) ----------------
def rep_many(buf,mapping,W=8):
    """simultaneous replace of 8-byte LE ids (old->new) so chains like a->b, b->c do not cascade"""
    b=bytes(buf); out=bytearray(b); 
    for old,new in mapping.items():
        ob=old.to_bytes(W,'little'); k=-1
        while True:
            k=b.find(ob,k+1)
            if k<0: break
            out[k:k+W]=new.to_bytes(W,'little')
    return out
def make_inst_fit(g,T,fit,nid,feat,idmap,outline_fn=None):
    """T: template of a Revit-made FamilyInstance; fit: {'rec':{'found':..},'item':{'found':..}}; feat: feature dict for the NEW instance;
    idmap: {old template id: new id} (host wall, levels, self); outline_fn(tpl_outline,hdr_log)->6 doubles"""
    W=8; idmap=dict(idmap); idmap[T['tid']]=nid
    assert fit.get('len') in (None,len(T['rec'])),('fit/template record length mismatch',fit.get('len'),len(T['rec']))
    L={n:(o,e) for n,o,e,_ in T['log']}
    rec=bytearray(T['rec']); 
    for off,(fn,co) in fit['rec']['found'].items(): struct.pack_into('<d',rec,int(off),sum(c*feat[f] for f,c in zip(fn,co)))
    rec=rep_many(rec,idmap); rec[4:12]=nid.to_bytes(W,'little')
    hdr=rep_many(T['hdr'],idmap); hl={n:(o,e) for n,o,e,_ in T['hlog']}
    if outline_fn: struct.pack_into('<6d',hdr,hl['Outline.m_minmax'][0],*outline_fn(struct.unpack_from('<6d',T['hdr'],hl['Outline.m_minmax'][0])))
    item=bytearray(T['item'])
    for off,(fn,co) in fit['item']['found'].items(): struct.pack_into('<d',item,int(off),sum(c*feat[f] for f,c in zip(fn,co)))
    item=rep_many(item,idmap)
    rec=bytearray(g.stamp(bytes(rec))); setphase(hdr); setphase(rec); rec=g.stamp(bytes(rec)); setphase(item); item=restamp(bytes(item),W)
    return bytes(hdr),bytes(rec),bytes(item)

# ---------------- plan view group (10 elements) cloned from rosetta/view_sheet_base ----------------
VIEW_GROUP=list(range(301554,301564))      # DBViewPlan,ExtentElem,Viewer,SunAndShadow,SunAnnotation,Viewport,DBDrawing,SketchGrid,SketchPlane(view),SketchPlane(level)
class ViewTpl:
    def __init__(self,gen,first=301553):
        off=first-301553; self.T=[gen.template(i+off) for i in VIEW_GROUP]; self.level=first
        assert self.T[0]['cls']=='DBViewPlan','view template ids moved'
def make_planview(g,VT,nids,level_id,z,name,zold=15.0):
    idmap={t['tid']:n for t,n in zip(VT.T,nids)}; idmap[VT.level]=level_id; out=[]
    for k,(t,nid) in enumerate(zip(VT.T,nids)):
        rec=bytearray(t['rec']); item=bytearray(t['item']); hdr=bytearray(t['hdr'])
        L={n:(o,e) for n,o,e,_ in t['log']}
        for buf in (rec,):
            for o in range(0,len(buf)-7):
                if struct.unpack_from('<d',buf,o)[0]==zold and o%1==0 and t['cls'] in('DBViewPlan','Viewer','SketchPlane'): struct.pack_into('<d',buf,o,z)
        rec=rep_many(rec,idmap); item=rep_many(item,idmap); hdr=rep_many(hdr,idmap)
        rec[4:12]=nid.to_bytes(8,'little')
        if t['cls']=='DBViewPlan':
            so,se=L['DBView.m_viewName']; rec[so:se]=genlib.ustr(name)
        rec=bytearray(g.stamp(bytes(rec))); item=restamp(bytes(item),8)
        row=bytearray(t['row']); row[0:8]=nid.to_bytes(8,'little'); row[20:28]=nid.to_bytes(8,'little')
        out.append((bytes(hdr),bytes(rec),bytes(item),nid,bytes(row)))
    return out

# ---------------- built-in instance parameters (Mark, Comments, ...) for elements that have a Double param set but no Int/AString sets (walls) ----------------
P_MARK=(1<<64)-1001203; P_COMMENTS=(1<<64)-1010106
PARAM_PTR={'int':3024,'str':3021}      # object-type ptr stored in the presence flag of ParamValueSetInt/AString (version specific; Scene overrides from the year's rosetta)
def add_params(rec,T,strings=None,ints=None):
    """rec: record bytes made from template T (same layout). Adds ParamValueSetInt / ParamValueSetAString blocks right after the Double set block.
    strings {param_id(u64 two's complement): text}, ints {param_id: int}. Only for templates whose Int and AString pointers are None."""
    L={n:(o,e,v) for n,o,e,v in T['log']}
    assert L['Element.m_pParamValueSetInt'][2]=='None' and L['Element.m_pParamValueSetAString'][2]=='None'
    end=L['ParamValueSetDouble.m_paramSet'][1]
    ip=L['Element.m_pParamValueSetInt'][0]; ap=L['Element.m_pParamValueSetAString'][0]
    blk=b''; flags_i=b''; flags_a=b''
    ints=ints or {}; strings=strings or {}
    if ints:
        blk+=struct.pack('<I',len(ints))+b''.join(struct.pack('<Qi',k,v) for k,v in ints.items())
    if strings:
        blk+=struct.pack('<I',len(strings))+b''.join(struct.pack('<Q',k)+struct.pack('<I',len(v))+v.encode('utf-16-le') for k,v in strings.items())
    r=bytearray(rec)
    r[end:end]=blk
    # pointer fields (later offsets first)
    if strings: r[ap:ap+4]=b'\xff\xff\xff\xff'+struct.pack('<H',PARAM_PTR['str'])
    if ints: r[ip:ip+4]=b'\xff\xff\xff\xff'+struct.pack('<H',PARAM_PTR['int'])
    return bytes(r)

def rep_str(buf,old,new):
    """replace a length-prefixed UTF-16 string ([u32 nchars][utf16]) old->new; returns bytearray (length may change)"""
    b=bytearray(buf); o=struct.pack('<I',len(old))+old.encode('utf-16-le'); k=b.find(o)
    while k>=0:
        b[k:k+len(o)]=struct.pack('<I',len(new))+new.encode('utf-16-le'); k=b.find(o,k+4+2*len(new))
    return b
SHEET_GROUP=list(range(301575,301581))      # ViewSheet(DBViewDrafting),Viewer,Viewport,DBDrawing,SketchPlane,TitleBlock FamilyInstance
class SheetTpl:
    def __init__(self,gen,first=301553):
        off=first-301553; self.T=[gen.template(i+off) for i in SHEET_GROUP]
        assert self.T[0]['cls']=='DBViewDrafting','sheet template ids moved'
def make_sheet(g,ST,nids,number,name):
    idmap={t['tid']:n for t,n in zip(ST.T,nids)}; out=[]
    for t,nid in zip(ST.T,nids):
        rec=rep_many(t['rec'],idmap); item=rep_many(t['item'],idmap); hdr=rep_many(t['hdr'],idmap)
        rec[4:12]=nid.to_bytes(8,'little')
        if t['cls']=='DBViewDrafting':
            rec=rep_str(rec,'A-900',number); rec=rep_str(rec,'Rosetta sheet',name)
        rec=bytearray(g.stamp(bytes(rec))); item=restamp(bytes(item),8)
        row=bytearray(t['row']); row[0:8]=nid.to_bytes(8,'little'); row[20:28]=nid.to_bytes(8,'little')
        out.append((bytes(hdr),bytes(rec),bytes(item),nid,bytes(row)))
    return out

# ---------------- project/shared parameter definitions (ParamElemExternal + ParamBinding) cloned from rosetta/params_wall_var ----------------
import uuid as _uuid
PARAM_KINDS={'text':301554,'int':301556,'number':301558,'length':301560,'yesno':301562}
class ParamTpl:
    def __init__(self,gen,first=301553):
        off=first-301553; self.PE={k:gen.template(i+off) for k,i in PARAM_KINDS.items()}; self.PBK={k:gen.template(i+1+off) for k,i in PARAM_KINDS.items()}
        assert all(t['cls']=='ParamElemExternal' for t in self.PE.values()),'param template ids moved'
def make_param(g,PT,kind,name,nid_pe,nid_pb,category_id=(1<<64)-2000011,guid=None):
    """returns [(hdr,rec,item,nid,row),..] for the definition and its binding (instance binding to one category, default Walls)"""
    T=PT.PE[kind]; PBT=PT.PBK[kind]; idmap={T['tid']:nid_pe,PBT['tid']:nid_pb}; out=[]
    L={n:(o,e) for n,o,e,_ in T['log']}
    # stored as Microsoft GUID bytes; deterministic (uuid5 of kind+name) so builds are reproducible and the same
    # parameter gets the same shared-parameter GUID in every file; a spec may pass its own GUID
    guid=(_uuid.UUID(guid) if guid else _uuid.uuid5(_uuid.UUID('6f1c3a52-8d0e-4b7a-9c41-2e5d7b9a0f13'),'%s:%s'%(kind,name))).bytes_le
    ob=T['rec'][L['GUIDvalue.m_guid'][0]:L['GUIDvalue.m_guid'][1]]
    rec=bytearray(T['rec']); rec[L['GUIDvalue.m_guid'][0]:L['GUIDvalue.m_guid'][1]]=guid
    # forge type id string 'revit.local.shared:<guid32>-1.0.0' (guid in canonical hex of the 16 stored bytes read as Microsoft GUID)
    old=None
    for n,o,e,v in T['log']:
        if n=='ForgeTypeId.m_typeId' and str(v).startswith('revit.local.shared'): old=(o,e,str(v))
    gtxt=str(_uuid.UUID(bytes_le=guid)).replace('-','')
    newt='revit.local.shared:%s-1.0.0'%gtxt
    co,ce=L['ParamDef.m_caption']
    # replace later field first so offsets stay valid
    segs=sorted([(old[0],old[1],genlib.ustr(newt)),(co,ce,genlib.ustr(name))],reverse=True)
    for a,b,new in segs: rec[a:b]=new
    rec=rep_many(rec,idmap); rec[4:12]=nid_pe.to_bytes(8,'little'); rec=bytearray(g.stamp(bytes(rec)))
    hdr=rep_many(T['hdr'],idmap); item=restamp(bytes(rep_many(T['item'],idmap)),8)
    row=bytearray(T['row']); row[0:8]=nid_pe.to_bytes(8,'little'); row[20:28]=nid_pe.to_bytes(8,'little'); out.append((bytes(hdr),bytes(rec),item,nid_pe,bytes(row)))
    B=PBT; r2=rep_many(B['rec'],idmap); r2[4:12]=nid_pb.to_bytes(8,'little')
    Lb={n:(o,e) for n,o,e,_ in B['log']}; r2[Lb['ParamBinding.m_categoryId'][0]:Lb['ParamBinding.m_categoryId'][1]]=category_id.to_bytes(8,'little')
    r2=bytearray(g.stamp(bytes(r2))); h2=rep_many(B['hdr'],idmap); i2=restamp(bytes(rep_many(B['item'],idmap)),8)
    row2=bytearray(B['row']); row2[0:8]=nid_pb.to_bytes(8,'little'); row2[20:28]=nid_pb.to_bytes(8,'little'); out.append((bytes(h2),bytes(r2),i2,nid_pb,bytes(row2)))
    return out
def add_values(rec,T,strings=None,ints=None,doubles=None):
    """extend add_params with doubles appended to the existing Double set (count bumped)."""
    L={n:(o,e,v) for n,o,e,v in T['log']}; doubles=doubles or {}
    r=bytearray(rec)
    if doubles:
        a,b,_=L['ParamValueSetDouble.m_paramSet']; n=struct.unpack_from('<I',r,a)[0]
        add=b''.join(struct.pack('<dQ',v,k) for k,v in doubles.items())
        r[b:b]=add; struct.pack_into('<I',r,a,n+len(doubles))
    T2=dict(T); 
    return add_params(bytes(r),dict(T,log=[(n,o,e+(len(r)-len(rec)) if n=='ParamValueSetDouble.m_paramSet' else e,v) for n,o,e,v in T['log']]) if doubles else T,strings=strings,ints=ints) if (strings or ints) else bytes(r)


def make_symbol_copy(g,T,newid):
    """clone the per-type FamilySymbol copy element (instance-info symbol) of a Revit-made file with a new id"""
    idb=newid.to_bytes(8,'little'); idmap={T['tid']:newid}
    rec=bytearray(rep_many(T['rec'],idmap)); rec[4:12]=idb; rec=bytearray(g.stamp(bytes(rec)))
    hdr=rep_many(T['hdr'],idmap); item=restamp(bytes(rep_many(T['item'],idmap)),8)
    row=bytearray(T['row']); row[0:8]=idb; row[20:28]=idb
    return bytes(hdr),bytes(rec),bytes(item),newid,bytes(row)


# ---------------- rooms (RoomElem + per-level LevelRoomPlan), fitted from rosetta/rooms_lv ----------------
def _rfeats(x0,y0,W,D,z):
    return {'1':1.0,'x0':x0,'y0':y0,'W':W,'D':D,'x1':x0+W,'y1':y0+D,'xm':x0+W/2,'ym':y0+D/2,'A':W*D,'P':2*(W+D),'z':z,'zt':z+9,
            'x0W':x0*W,'y0W':y0*W,'x0D':x0*D,'y0D':y0*D,'W2':W*W,'D2':D*D,'x1D':(x0+W)*D,'y1W':(y0+D)*W,'x1y1':(x0+W)*(y0+D),'x0y0':x0*y0,'hA':W*D/2}
class RoomTpl:
    def __init__(self,gen,room_id,plan_id,level_id,wall_ids,year=2024):
        self.year=year; self.R=gen.template(room_id); self.P=gen.template(plan_id); self.level=level_id; self.walls=wall_ids
def make_room(g,RT,nids,wall_ids,level_id,x0,y0,W,D,z,name,number):
    """nids=(room,plan); wall_ids = 4 new wall ids in creation order bottom,right,top,left"""
    fit=_json.load(open(os.path.expanduser('~/rvt-research/write-lab/files/roomfit%s.json'%('' if getattr(RT,'year',2024)==2024 else '_%d'%RT.year))))
    ft=_rfeats(x0,y0,W,D,z); idmap={RT.R['tid']:nids[0],RT.P['tid']:nids[1],RT.level:level_id}
    for a,b in zip(RT.walls,wall_ids): idmap[a]=b
    out=[]
    for T,nid,tag in ((RT.R,nids[0],'room'),(RT.P,nids[1],'plan')):
        parts={}
        for key in ('rec','hdr','item'):
            b=bytearray(T[key]); fd=(fit.get(tag+'.'+key) or {}).get('found',{})
            for off,(fn,co) in fd.items(): struct.pack_into('<d',b,int(off),sum(c*ft[f] for f,c in zip(fn,co)))
            parts[key]=bytearray(rep_many(b,idmap))
        rec=parts['rec']; rec[4:12]=nid.to_bytes(8,'little')
        if tag=='room':
            rec=rep_str(rec,'0',number); rec=rep_str(rec,'RR0',name)
        rec=bytearray(g.stamp(bytes(rec))); hdr=parts['hdr']; item=restamp(bytes(parts['item']),8)
        row=bytearray(T['row']); row[0:8]=nid.to_bytes(8,'little'); row[20:28]=nid.to_bytes(8,'little')
        out.append((bytes(hdr),bytes(rec),item,nid,bytes(row)))
    return out

# ---------------- walls WITH hosted windows (cut openings), cloned+fitted from rosetta/walls_open_k2 (60 ft walls along +x, level 1, one window type) ----------------
class OpenWallTpl:
    def __init__(self,gen,tag='walls_open_k2_base',Y=2024):
        rows=[l.rstrip('\n').split('\t') for l in open(os.path.expanduser('~/rvt-research/gt_geom/%d_%s.tsv'%(Y,tag)),errors='replace')]
        import re as _re
        walls=[int(r[1]) for r in rows if r[0]=='EL' and r[2]=='Wall']
        fin={r[1]:[float(v) for v in _re.search(r'transform=([^;]*)',' '.join(r)).group(1).split(',')] for r in rows if r[0]=='FINST'}
        cat={r[1]:r[3] for r in rows if r[0]=='EL'}
        wins={}
        for i,xyz in fin.items():
            if cat.get(i)=='Windows': wins.setdefault(round(xyz[1]),[]).append((xyz[0],int(i)))
        self.by_k={}; self.fit=_json.load(open(os.path.expanduser('~/rvt-research/write-lab/files/openfit_%s.json'%tag))); self.wfit=_json.load(open(os.path.expanduser('~/rvt-research/write-lab/files/winfit_open.json')))
        for w in walls:
            T=gen.template(w); wl=[r for r in rows if r[0]=='WALLLOC' and r[1]==str(w)][0]
            m=_re.findall(r'(-?[0-9.eE+-]+),(-?[0-9.eE+-]+),(-?[0-9.eE+-]+)',wl[2]); y=float(m[0][1]); ws=sorted(wins.get(round(y),[]))
            k=len(ws)
            reg=int(y>256.0)
            if k and (k,reg) not in self.by_k:
                tw=[gen.template(i) for x,i in ws]
                if all(len(t['rec'])==581 for t in tw): self.by_k[(k,reg)]=(T,tw,y,[x for x,i in ws])
def make_wall_open(g,OW,nid_wall,nids_win,y,xs,tr):
    assert not (252.0<y<259.0),'opening-wall geometry straddles the 256 ft record regime boundary (unsupported)'
    assert not (len(xs)==4 and y>256.0),'4-window opening walls beyond y=256 ft are not reliable (5 of 8 sweep walls came out corrupt)'
    k=len(xs); reg=int(y>256.0); T,TW,ty,txs=OW.by_k[(k,reg)]; fit=OW.fit[str(k)]
    feat={'1':1.0,'y':y}; 
    for j,x in enumerate(xs): feat['x%d'%(j+1)]=x
    idmap={T['tid']:nid_wall}; idmap.update({t['tid']:n for t,n in zip(TW,nids_win)})
    parts={}
    for key in ('rec','hdr','item'):
        b=bytearray(T[key])
        for off,(fn,co) in (fit[key] or {}).get('found',{}).items(): struct.pack_into('<d',b,int(off),sum(c*feat[f] for f,c in zip(fn,co)))
        parts[key]=bytearray(rep_many(b,idmap))
    rec=parts['rec']; rec[4:12]=nid_wall.to_bytes(8,'little'); hdr=parts['hdr']; item=parts['item']
    setphase(hdr); setphase(rec); rec=bytearray(g.stamp(bytes(rec))); setphase(item); item=restamp(bytes(item),8)
    row=bytearray(T['row']); row[0:8]=nid_wall.to_bytes(8,'little'); row[20:28]=nid_wall.to_bytes(8,'little'); struct.pack_into('<3I',row,8,*tr)
    out=[(bytes(hdr),bytes(rec),item,nid_wall,bytes(row))]
    for j,(t,nid) in enumerate(zip(TW,nids_win)):
        L={n:(o,e) for n,o,e,_ in t['log']}
        ox,oy,oz=struct.unpack_from('<3d',t['rec'],L['FamilyInstance.m_instOrigin'][0]); x=xs[j]
        f2={'1':1.0,'x':x,'y':y,'z':oz,'hp':x,'lz':0.0,'zr':oz}
        def ol(o,x=x,y=y,ox=ox,oy=oy): return (o[0]+x-ox,o[1]+y-oy,o[2],o[3]+x-ox,o[4]+y-oy,o[5])
        hd,rc,it=make_inst_fit(g,t,OW.wfit,nid,f2,{T['tid']:nid_wall},ol)
        r=bytearray(t['row']); r[0:8]=nid.to_bytes(8,'little'); r[20:28]=nid.to_bytes(8,'little'); struct.pack_into('<3I',r,8,*tr)
        out.append((hd,rc,it,nid,bytes(r)))
    return out

# ---------------- topography: the rosetta 5-point hill translated in x,y (contours are shifted too); offsets learnt from rosetta/topography_shift base vs var (+100,+50) ----------------
class TopoTpl:
    def __init__(self,genb,genv,first):
        self.T=genb.template(first); V=genv.template(first); self.X={}; self.Y={}
        for key in ('rec','item','hdr'):
            a,b=self.T[key],V[key]; xs=[];ys=[]
            for o in range(0,len(a)-7):
                x=struct.unpack_from('<d',a,o)[0]; y=struct.unpack_from('<d',b,o)[0]
                if x==x and y==y and abs(x)<1e5 and abs(y)<1e5:
                    if abs(y-x-100)<1e-6: xs.append(o)
                    elif abs(y-x-50)<1e-6: ys.append(o)
            self.X[key]=xs; self.Y[key]=ys
def make_topo(g,TP,nid,dx,dy):
    T=TP.T; idmap={T['tid']:nid}; parts={}
    for key in ('rec','item','hdr'):
        b=bytearray(T[key])
        for o in TP.X[key]: struct.pack_into('<d',b,o,struct.unpack_from('<d',b,o)[0]+dx)
        for o in TP.Y[key]: struct.pack_into('<d',b,o,struct.unpack_from('<d',b,o)[0]+dy)
        parts[key]=bytearray(rep_many(b,idmap))
    rec=parts['rec']; rec[4:12]=nid.to_bytes(8,'little'); hdr=parts['hdr']; setphase(hdr); setphase(rec); rec=bytearray(g.stamp(bytes(rec))); item=parts['item']; setphase(item); item=restamp(bytes(item),8)
    row=bytearray(T['row']); row[0:8]=nid.to_bytes(8,'little'); row[20:28]=nid.to_bytes(8,'little')
    return bytes(hdr),bytes(rec),item,nid,bytes(row)

# ---------------- viewport placing a plan view on a sheet (2026; fields decoded from rosetta/2026_sheet_viewport_{base,var}, positions fitted from sheet_viewport_pos) ----------------
def hdr_list_add(hdr,hlog,adds,W=8):
    """hdr: ElementHeader bytes [id][Lh]...; hlog: decoded field log of the SAME bytes; adds {field name: [ids]} appended (sorted, unique) to those id lists; Lh updated"""
    L={n:(o,e) for n,o,e,_ in hlog}; h=bytearray(hdr)
    for fld,ids in sorted(adds.items(),key=lambda kv:-L[kv[0]][0]):
        o,e=L[fld]; n=struct.unpack_from('<I',h,o)[0]; cur=[int.from_bytes(h[o+4+W*k:o+4+W*(k+1)],'little') for k in range(n)]
        lst=sorted(set(cur)|set(ids)); h[o:e]=struct.pack('<I',len(lst))+b''.join(i.to_bytes(W,'little') for i in lst)
    struct.pack_into('<I',h,W,len(h)-W-4); return bytes(h)
class VportTpl:
    def __init__(self,gen):
        new=[i for i in sorted(set(gen.e.m.ids)) if i>=301553 and gen.e.trace(i)[2]['class']=='Viewport']
        T=None
        for i in new:
            t=gen.template(i); Lv={n:v for n,o,e,v in t['log']}
            if 'Viewport.m_dbViewId' in Lv and str(Lv['Viewport.m_dbViewId'])!='EID(18446744073709551615)' and str(Lv['Element.m_ownerDBViewId'])!='EID(18446744073709551615)' and float(str(Lv['Viewport.m_scale']))>0: T=t
        assert T,'no placed viewport in template file'
        self.T=T; L={n:(o,e,v) for n,o,e,v in T['log']}; self.L=L
        gid=lambda n: int(re_eid(L[n][2]))
        self.plan=gid('Viewport.m_dbViewId'); self.sheet=gid('Element.m_ownerDBViewId'); self.draw=gid('Viewport.m_dbDrawingId')
        hl={n:v for n,o,e,v in T['hlog']}; import re as _re; ro=[int(x) for x in _re.findall(r'EID\((\d+)\)',str(hl['ElementParents.m_regenOnly']))]; self.viewer=[i for i in ro if i>self.plan][0]
        import ast as _ast; _v=lambda x: _ast.literal_eval(x) if isinstance(x,str) else x
        self.off=_v(L['Viewport.m_offset'][2]); self.lab=_v(L['Viewport.m_labelOrigin'][2]); self.scale=float(str(L['Viewport.m_scale'][2]))
        # model centre implied by the template placement (sheet = offset + scale*model): used when the caller gives none
        self.mc=None
def re_eid(v):
    import re as _re; return _re.search(r'(\d+)',str(v)).group(1)
def make_viewport(g,VP,nid,plan_id,viewer_id,sheet_id,draw_id,centre,model_centre,detail='1'):
    """returns (hdr,rec,item,row) of the new Viewport; caller patches plan/viewer/sheet/drawing (see patch_for_viewport)"""
    T=VP.T; idmap={T['tid']:nid,VP.plan:plan_id,VP.sheet:sheet_id,VP.draw:draw_id,VP.viewer:viewer_id}
    rec=rep_many(T['rec'],idmap); hdr=rep_many(T['hdr'],idmap); item=rep_many(T['item'],idmap)
    rec[4:12]=nid.to_bytes(8,'little')
    s=VP.scale; ox=centre[0]-s*model_centre[0]; oy=centre[1]-s*model_centre[1]
    L=VP.L; o=L['Viewport.m_offset'][0]; struct.pack_into('<3d',rec,o,ox,oy,0.0)
    o=L['Viewport.m_labelOrigin'][0]; struct.pack_into('<3d',rec,o,ox+VP.lab[0]-VP.off[0],oy+VP.lab[1]-VP.off[1],0.0)
    o,e,_=L['Viewport.m_detailNumber']; rec[o:e]=struct.pack('<I',len(detail))+detail.encode('utf-16-le')
    rec=bytearray(g.stamp(bytes(rec))); item=restamp(bytes(item),8)
    row=bytearray(T['row']); row[0:8]=nid.to_bytes(8,'little'); row[20:28]=nid.to_bytes(8,'little')
    return bytes(hdr),bytes(rec),bytes(item),bytes(row)

# ---------------- view-owned annotations (2026 templates from rosetta/2026_view_k_annotations_var: detail line, text note) ----------------
class AnnoTpl:
    def __init__(self,gen):
        new=[i for i in sorted(set(gen.e.m.ids)) if i>=301553]
        cls={i:gen.e.trace(i)[2]['class'] for i in new}
        self.view=None; self.T={}
        for i in new:
            if cls[i]=='TextNote' and 'text' not in self.T: self.T['text']=gen.template(i)
            if cls[i]=='CurveElem' and 'dline' not in self.T:
                t=gen.template(i); Lv={n:v for n,o,e,v in t['log']}
                if str(Lv.get('CurveElem.m_detail'))=='1' and len(t['item'])==244: self.T['dline']=t
        import re as _re
        g=lambda t,n: int(_re.search(r'(\d+)',str({a:v for a,o,e,v in t['log']}[n])).group(1))
        self.view=g(self.T['dline'],'Element.m_ownerDBViewId'); self.sp=g(self.T['dline'],'CurveElem.m_sketchPlaneId')
        assert g(self.T['text'],'Element.m_ownerDBViewId')==self.view
def make_detail_line(g,AT,nid,plan_id,sp_id,p0,p1,z,triple):
    T=AT.T['dline']; hd,rec,it,row=genlib.make_line(g,T,nid,sp_id,p0,p1,z,triple,Tsp=AT.sp)
    m={AT.view:plan_id}; hd=rep_many(hd,m); rec=rep_many(rec,m); it=rep_many(it,m)
    return bytes(hd),g.stamp(bytes(rec)),restamp(bytes(it),8),row
def make_view_text(g,AT,nid,plan_id,x,y,z,text):
    T=AT.T['text']; hd,rec,it=make_textnote(g,T,nid,x,y,text,z=z)
    L={n:(o,e) for n,o,e,_ in T['log']}
    m={AT.view:plan_id,T['tid']:nid}; hd=rep_many(hd,m); rec=rep_many(rec,m); it=rep_many(it,m)
    return bytes(hd),g.stamp(bytes(rec)),restamp(bytes(it),8)

# ---------------- grids (straight): DatumPlane with a vertical Plane (origin = start, xVec = direction, envelope u 0..length) x2 copies; from rosetta/<year>_grid_level_base ----------------
def grid_template(gen):
    """straight grid with the smallest header (2026: the first grid's header carries regen-history/list entries naming the other rosetta grids)"""
    c=[]
    for i in sorted(set(gen.e.m.ids)):
        if i>=301553 and gen.e.trace(i)[2]['class']=='Grid':
            t=gen.template(i)
            if sum(1 for n,o,e,v in t['log'] if n=='Plane.m_origin')==2 and 'GArc' not in str([n for n,o,e,v in t['log']]): c.append(t)
    m=os.environ.get('GRID_TPL','min')
    if m=='first': return c[0]
    if m=='last': return c[-1]
    return min(c,key=lambda t:(len(t['hdr']),t['tid']))
def make_grid(g,T,nid,name,p0,p1,triple):
    W=8; idb=nid.to_bytes(W,'little'); rec=bytearray(T['rec']); L=T['log']
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; ln=math.hypot(dx,dy)
    for n,o,e,v in L:
        if n=='Plane.m_origin': z=struct.unpack_from('<3d',rec,o)[2]; struct.pack_into('<3d',rec,o,p0[0],p0[1],z)
        if n=='Plane.m_xVec': struct.pack_into('<3d',rec,o,dx/ln,dy/ln,0.0)
        if n=='Envelope.m_corners': c=struct.unpack_from('<4d',rec,o); struct.pack_into('<4d',rec,o,0.0,c[1],ln,c[3])
    so,se=[(o,e) for n,o,e,v in L if n=='DatumPlane.m_text'][0]
    rec=rep_many(rec,{T['tid']:nid}); rec[so:se]=genlib.ustr(name); rec[4:12]=idb
    hdr=rep_many(T['hdr'],{T['tid']:nid}); item=rep_many(T['item'],{T['tid']:nid})
    if os.environ.get('GRID_NOHIST','1')=='1':           # drop the regen-history map (episode ids of the rosetta session; empty in a freshly loaded element)
        ho,he=[(o,e) for n,o,e,v in T['hlog'] if n=='ElementRegenHistory.m_historyMap'][0]
        if he-ho>4: hdr[ho:he]=struct.pack('<I',0); struct.pack_into('<I',hdr,W,len(hdr)-W-4)
    return bytes(hdr),g.stamp(bytes(rec)),restamp(bytes(item),W),_row(g,T,nid,W,triple)

# ---------------- generic import of self-contained Revit records (e.g. types copied into a rosetta by CopyElements) ----------------
def import_elements(g,src,ids,nids,extra=None):
    """clone elements `ids` of rvtgen.Gen `src` (same seed as g) as new ids `nids`; every reference among them is remapped; extra {old:new} remaps
    other references (must point to elements that exist in g). returns [(hdr,rec,item,nid,row)]"""
    idmap=dict(zip(ids,nids)); idmap.update(extra or {}); out=[]
    for i,nid in zip(ids,nids):
        t=src.template(i); rec=rep_many(t['rec'],idmap); hdr=rep_many(t['hdr'],idmap); item=rep_many(t['item'],idmap)
        rec[4:12]=nid.to_bytes(8,'little'); rec=bytearray(g.stamp(bytes(rec))); item=restamp(bytes(item),8)
        row=rep_many(t["row"],idmap); out.append((bytes(hdr),bytes(rec),bytes(item),nid,bytes(row)))
    return out

# ---------------- translated copies of any Revit-made object group (stairs, railings, curtain walls, ...): learnt from a *_shift rosetta pair (var = base + (100,50,0)) ----------------
class GroupShiftTpl:
    def __init__(self,genb,genv,seed_ids,DX=100.0,DY=50.0):
        self.ids=sorted(set(genb.e.m.ids)-set(seed_ids)); assert self.ids==sorted(set(genv.e.m.ids)-set(seed_ids)),'base/var id sets differ'
        self.T={}; self.X={}; self.Y={}; self.unexpl={}; self.shared=[]
        for i in self.ids:
            a=genb.template(i); b=genv.template(i); self.T[i]=a
            if a['rec']==b['rec'] and a['hdr']==b['hdr'] and a['item']==b['item'] and a['cls'].endswith(('Type','Symbol')): self.shared.append(i)
            for key in ('rec','item','hdr','row'):
                A,B=a[key],b[key]; assert len(A)==len(B),'length differs %d %s'%(i,key)
                xs=[];ys=[]; cov=set()
                for o in range(0,len(A)-7):
                    x=struct.unpack_from('<d',A,o)[0]; y=struct.unpack_from('<d',B,o)[0]
                    if x==x and y==y and abs(x)<1e6 and abs(y)<1e6 and A[o:o+8]!=B[o:o+8]:
                        if abs(y-x-DX)<1e-6: xs.append(o); cov.update(range(o,o+8))
                        elif abs(y-x-DY)<1e-6: ys.append(o); cov.update(range(o,o+8))
                self.X[(i,key)]=xs; self.Y[(i,key)]=ys
                un=[o for o in range(len(A)) if A[o]!=B[o] and o not in cov and not (key=='rec' and o<12) and not (key=='item' and 8<=o<12)]
                if un: self.unexpl[(i,key)]=un
def make_group_shift(g,GT,nids,dx,dy,tr,reuse=None):
    """nids: one new id per GT.ids entry; reuse {template shared id: id already in g}: those elements (types) are not created again, references go to the earlier copy"""
    reuse=reuse or {}; idmap=dict(zip(GT.ids,nids)); idmap.update(reuse); out=[]
    for i,nid in zip(GT.ids,nids):
        if i in reuse: continue
        T=GT.T[i]; parts={}
        for key in ('rec','item','hdr','row'):
            b=bytearray(T[key])
            for o in GT.X[(i,key)]: struct.pack_into('<d',b,o,struct.unpack_from('<d',b,o)[0]+dx)
            for o in GT.Y[(i,key)]: struct.pack_into('<d',b,o,struct.unpack_from('<d',b,o)[0]+dy)
            parts[key]=bytearray(rep_many(b,idmap))
        rec=parts['rec']; rec[4:12]=nid.to_bytes(8,'little'); setphase(parts['hdr']); setphase(rec); setphase(parts['item']); genlib.rekey_item(parts['item'],T,parts['hdr'])   # Phase 1 like the rest + spatial pick key of the moved outline
        rec=g.stamp(bytes(rec)); item=restamp(bytes(parts['item']),8)
        row=parts['row']; struct.pack_into('<3I',row,8,*tr)
        out.append((bytes(parts['hdr']),rec,item,nid,bytes(row)))
    return out

# ---------------- free-size flat roof + ceiling: clone of the roof_shift group, doubles set from the roofs12 size fit (files/rooffit_2024.json) ----------------
ROOF_FIRST={2024:301628,2026:303764}; ROOF_ID0={2024:301628,2026:303764}; _ROOF_CANON={}
def roof_canon(year,portrait=False):
    """{item offset: 'W'|'D'|'0'} of the ProfileRoof item's edge-block area, read from sample 0 (40 x 26 ft, W>D) of rosetta <year>_roofs12_base"""
    k=(year,portrait)
    if k not in _ROOF_CANON:
        import rvtgen
        nm,fit,(vw,vd)=('roofs12p','rooffit3p',(26.0,40.0)) if portrait else ('roofs12','rooffit',(40.0,26.0))
        g=rvtgen.Gen(os.path.expanduser('~/rvt-research/rosetta/%d_%s_base.rte'%(year,nm))); it=g.template(ROOF_ID0[year])['item']; c={}
        un=[int(o) for o in _json.load(open(os.path.expanduser('~/rvt-research/write-lab/files/%s_%d.json'%(fit,year))))['roles']['0']['item']['unexpl']]
        for o in un:
            v=struct.unpack_from('<d',it,o)[0]
            if v==vw: c[o]='W'
            elif v==vd: c[o]='D'
            elif v==0.0: c[o]='0'
        _ROOF_CANON[k]=c
    return _ROOF_CANON[k]
ROOF_CANON_OLD= ROOF_CANON=[((0,8,16,32,40),'WDDW0'),((0,8,16,32,40),'0DWWD'),((0,8,16,32,40),'00D0D'),((0,8,16,32,40),'W0W00'),((0,8,32,40,48),'00W0W'),((0,8,32,40,48),'WD0DW'),((0,8,32,40,48),'W0WDD'),((0,8,32,40,48),'0D00D')]
def make_roof_group(g,GT,nids,x0,y0,W,D,tr,reuse,year=2024,level=355,z=0.0):
    """GT/nids as make_group_shift (roof_shift group); every record of role r (id - first roof id; the ceiling sketch plane/sketch before the roof = roles 22,23) gets the fitted doubles for the rectangle (x0,y0,W,D), W>D.
    Offsets the fit could not explain keep the template bytes (they are the same stale per-sample value in every Revit record), except the 8 edge blocks of the ProfileRoof item, written in Revit's canonical block order."""
    assert W!=D, 'free-size roofs need W != D (square roofs are a different regime)'
    port=D>W
    fit=_json.load(open(os.path.expanduser('~/rvt-research/write-lab/files/%s_%d.json'%('rooffit3p' if port else 'rooffit',year))))['roles']
    try: fit.update({str(k):v for k,v in _json.load(open(os.path.expanduser('~/rvt-research/write-lab/files/rooffit_2223_%d.json'%year))).items()})
    except FileNotFoundError: pass
    first=ROOF_FIRST[year]; ft=_ffeats(x0,y0,W,D); ft.update(W2=W*W,D2=D*D,diag=(W*W+D*D)**0.5)
    idmap=dict(zip(GT.ids,nids)); idmap.update(reuse); out=[]
    if level!=355: idmap[355]=level
    for i,nid in zip(GT.ids,nids):
        if i in reuse: continue
        r=i-first if i>=first else {i_:22+k for k,i_ in enumerate([j for j in GT.ids if j<first and j>first-5])}.get(i)
        T=GT.T[i]; parts={}
        for key in ('rec','item','hdr','row'):
            b=bytearray(T[key])
            if key!='row' and r is not None and str(r) in fit:
                for off,(fn,co) in ((fit[str(r)].get(key) or {}).get('found') or {}).items(): struct.pack_into('<d',b,int(off),sum(c*ft[f] for f,c in zip(fn,co)))
            if z and r is not None and str(r) in fit:
                for off,sl in ((fit[str(r)].get('zslope') or {}).get(key) or {}).items():
                    if isinstance(sl,(int,float)) and sl: struct.pack_into('<d',b,int(off),struct.unpack_from('<d',b,int(off))[0]+sl*z)
            if key=='item' and r==0:
                for o,sym in roof_canon(year,port).items(): struct.pack_into('<d',b,o,{'W':W,'D':D,'0':0.0}[sym])
            parts[key]=bytearray(rep_many(b,idmap))
        rec=parts['rec']; rec[4:12]=nid.to_bytes(8,'little'); setphase(parts['hdr']); setphase(rec); setphase(parts['item']); genlib.rekey_item(parts['item'],T,parts['hdr'])
        rec=g.stamp(bytes(rec)); item=restamp(bytes(parts['item']),8)
        row=parts['row']; struct.pack_into('<3I',row,8,*tr)
        out.append((bytes(parts['hdr']),rec,item,nid,bytes(row)))
    return out

# ---------------- grid registry in Global/Latest (2 lists: grid list after two negative ids, and the datum list levels+grids, both sorted id lists) ----------------
def grid_anchors(year):
    """learn from rosetta <year>_grid_level_base vs the year's ds0 seed: for both lists the 24-byte context before the u32 count, and the number of
    leading seed ids. returns [(ctx, n_seed_ids)]"""
    import adiff
    R=os.path.expanduser('~/rvt-research/rosetta/%d_grid_level_base.rte'%year); seedf=os.path.expanduser('~/rvt-research/write-lab/files/'+{2024:'ds0.rte',2026:'o26_line.rte'}[year])
    b=adiff.graw(R,'Global/Latest'); a=adiff.graw(seedf,'Global/Latest'); first={2024:301553,2026:303689}[year]
    import wledit; sid=set(wledit.Editor(seedf).m.ids)
    out=[]; k=b.find(struct.pack('<Q',first))
    while k>=0:
        j=k; n=0
        while struct.unpack_from('<Q',b,j-8)[0] in sid: j-=8; n+=1
        if n:
            key=struct.pack('<I',n)+bytes(b[j:j+8*n]); occ=[]; q=a.find(key)
            while q>=0: occ.append(q); q=a.find(key,q+1)
            assert occ,'datum list not in seed'
            best=min(range(len(occ)),key=lambda t:abs(occ[t]-(j-4)) if occ[t]<=j-4 else 1e9)   # closest seed occurrence at or before (grids only add bytes)
            out.append(('ids',key,best)); k=b.find(struct.pack('<Q',first),k+1); continue
        for L in (24,40,64,96):
            ctx=bytes(b[j-4-L:j-4]); ka=a.find(ctx)
            if ka>=0 and a.find(ctx,ka+1)<0: break
        assert ka>=0 and a.find(ctx,ka+1)<0,'grid anchor context not unique'
        assert struct.unpack_from('<I',a,ka+len(ctx))[0]==n,('seed count mismatch',n)
        out.append(('ctx',ctx,n)); k=b.find(struct.pack('<Q',first),k+1)
    return out
def grid_registry(raw,anchors,ids):
    """append grid ids to both lists (after whatever ids the list holds now: call AFTER the level patch, grid ids are larger)"""
    out=bytearray(raw)
    for kind,key,n in anchors:
        if kind=='ctx': k=out.find(key)+len(key)
        else:          # key = u32 seed count + seed ids; n = occurrence index. Locate by the ids (the count may already be bumped by the level patch)
            ids0=key[4:]; occ=[]; q=out.find(ids0)
            while q>=0: occ.append(q); q=out.find(ids0,q+1)
            k=occ[n]-4
        cnt=struct.unpack_from('<I',out,k)[0]; end=k+4+8*cnt
        cur=[struct.unpack_from('<Q',out,k+4+8*j)[0] for j in range(cnt)]; merged=sorted(cur+list(ids))      # lists are kept sorted by id
        out[k:end]=struct.pack('<I',len(merged))+b''.join(struct.pack('<Q',i) for i in merged)
    return bytes(out)

def set_last_grid_name(raw,name):
    """Global/Latest keeps 'last used name' cells: ..., 'Level 6', <grid cell>, 'Section 0', ...: the grid cell holds the last grid name ('0' in a fresh house).
    Revit rewrites it to the newest grid's name; seeds that have this table (2026 house_base) refuse files where grids exist but the cell still says '0'. returns raw unchanged if the pattern is absent"""
    sec=struct.pack('<I',9)+'Section 0'.encode('utf-16-le'); k=raw.find(sec)
    if k<0 or raw.find(sec,k+1)>=0: return raw
    for n in range(1,24):
        s=k-28-(4+2*n)
        if s>0 and struct.unpack_from('<I',raw,s)[0]==n and all(raw[s+5+2*j]==0 and 32<=raw[s+4+2*j]<127 for j in range(n)):
            out=bytearray(raw); out[s:s+4+2*n]=struct.pack('<I',len(name))+name.encode('utf-16-le'); return bytes(out)
    return raw

# ---------------- JOINED rectangle of 4 walls (Revit-made joins: CurveDriver join info + JoinEnd geom steps), fitted from rosetta rooms_lv ----------------
# Revit only encloses a room by walls that are joined at the corners; writer walls were never joined (rooms had area 0).
# files/joinwallfit_<year>.json (tools/fit_joinwalls.py): per wall role (bottom, right, top, left) the doubles of rec/hdr/item as linear
# functions of the rectangle (x0,y0,W,D,z); wall height is the rosetta's 9 ft.
class JoinRectTpl:
    def __init__(self,year):
        self.F=_json.load(open(os.path.expanduser('~/rvt-research/write-lab/files/joinwallfit_%d.json'%year)))
        import rvtgen
        g=rvtgen.Gen(os.path.expanduser('~/rvt-research/rosetta/%d_rooms_lv_base.rte'%year))
        self.T=[g.template(r['tpl']) for r in self.F['roles']]; self.ids=self.F['ids']
def make_joined_rect(g,JT,wall_nids,level_id,x0,y0,W,D,z,extra_map=None):
    """4 joined walls (bottom,right,top,left) around (x0,y0)-(x0+W,y0+D) on level level_id (elevation z). extra_map: more template->new id
    pairs (room/plan of the template rectangle). returns [(hdr,rec,item,nid,row)]"""
    ft=_rfeats(x0,y0,W,D,z); idmap=dict(zip(JT.ids['walls'],wall_nids)); idmap[JT.ids['level']]=level_id; idmap.update(extra_map or {})
    out=[]
    for role,(T,nid) in enumerate(zip(JT.T,wall_nids)):
        fr=JT.F['roles'][role]; parts={}
        for key in ('rec','hdr','item'):
            b=bytearray(T[key])
            for off,(fn,co) in ((fr.get(key) or {}).get('found',{})).items(): struct.pack_into('<d',b,int(off),sum(c*ft[f] for f,c in zip(fn,co)))
            parts[key]=bytearray(rep_many(b,idmap))
        rec=parts['rec']; rec[4:12]=nid.to_bytes(8,'little'); setphase(parts['hdr']); setphase(rec); setphase(parts['item'])
        genlib.rekey_item(parts['item'],T,parts['hdr'])
        rec=bytearray(g.stamp(bytes(rec))); item=restamp(bytes(parts['item']),8)
        row=bytearray(rep_many(T['row'],idmap)); row[0:8]=nid.to_bytes(8,'little')
        out.append((bytes(parts['hdr']),bytes(rec),item,nid,bytes(row)))
    return out

# ---------------- linear dimensions between the faces of two parallel walls (template: rosetta/<year>_view_dims_fit_var; V = dim line along x at y=c, H = along y at x=c) ----------------
DIM_K=0.695971241325342   # offset of the witness reference points from the dimension line (V: y=c+K, H: x=c-K), constant in the rosetta (15 dims)
class DimTpl:
    def __init__(self,gen):
        new=[i for i in sorted(set(gen.e.m.ids)) if i>=301553 and gen.e.trace(i)[2]['class']=='LinearDimString']
        self.T=gen.template(new[4])          # V dim at y=7
        self.view=None; self.walls=None
        L=self.T['log']; import re as _re
        gi=lambda n,k=0: [o for nn,o,e,v in L if nn==n][k]
        self.view=int(_re.search(r'(\d+)',str([v for n,o,e,v in L if n=='Element.m_ownerDBViewId'][0])).group(1))
        self.wA=int(_re.search(r'(\d+)',str([v for n,o,e,v in L if n=='GeomRef.m_elemId'][0])).group(1)); self.wB=int(_re.search(r'(\d+)',str([v for n,o,e,v in L if n=='GeomRef.m_elemId'][1])).group(1))
        self.gi=gi
def make_dimension(g,DT,nid,plan_id,wA,wB,axis,fa,fb,ca,cb,c,z,triple):
    """axis 'V': dimension line along x at y=c between faces x=fa and x=fb; 'H': along y at x=c between faces y=fa and y=fb (fa<fb).
    ca,cb = (start,end) of the face of wall A/B along the other axis in the wall's own direction (face segment ends). wA,wB = wall ids with face fa/fb"""
    T=DT.T; m={DT.view:plan_id,T['tid']:nid}; rec=bytearray(rep_many(T['rec'],m)); gi=DT.gi;   # remap ids FIRST: inserted wall ids may equal a template id
    V=(axis=='V'); pk=lambda o,*v: struct.pack_into('<%dd'%len(v),rec,o,*v)
    var=os.environ.get('DIM_VARIANT','')
    if var=='raw': m={DT.view:plan_id,T['tid']:nid}; rec=rep_many(T['rec'],m); rec=bytearray(rec); rec[4:12]=nid.to_bytes(8,'little'); return bytes(rep_many(T['hdr'],m)),g.stamp(bytes(rec)),restamp(bytes(rep_many(T['item'],m)),8),_row(g,T,nid,8,triple)
    k=DIM_K if V else -DIM_K; val=fb-fa; mid=(fa+fb)/2
    P=lambda a,s: (a,s,z) if V else (s,a,z)               # face coordinate a (x for V), along coordinate s (y for V)
    # witness points
    def pt(face,s): return (face,s,z) if V else (s,face,z)
    ON=lambda n: (not os.environ.get('DIM_ONLY')) or n in os.environ['DIM_ONLY'].split(',')
    r0=gi('Dimension.m_refPnts')+4;   # 4-byte count prefix
    if ON('refp'): pk(r0,*( (fa,c+k,z)+(fb,c+k,z) )) if V else pk(r0,*((c+k,fa,z)+(c+k,fb,z)))
    for n in (('DimSegInfo.m_lockedValue','DimSegValue.m_value') if ON('val') else ()): pk(gi(n,0),val)
    if ON('origin'): pk(gi('DimSegInfo.m_origin'),*((mid,c,z) if V else (c,mid,z)))
    if ON('old'): pk(gi('Dimension.m_oldOrigin'),*((0.0,c,z) if V else (c,0.0,z)))
    if ON('gline'): pk(gi('GLine.m_origin'),*((0.0,c,z) if V else (c,0.0,z))); pk(gi('GLine.m_dirVec'),*((1.0,0.0,0.0) if V else (0.0,1.0,0.0)))
    for w,(face,(s0,s1)) in enumerate(((fa,ca),(fb,cb)) if ON('wit') else ()):
        near=0 if abs(c-s0)<=abs(c-s1) else 1                    # nearest face end first (tie: the wall's start); idx = its index in the wall's own direction
        a_,b_=((s0,s1) if near==0 else (s1,s0))
        o=gi('WitnessRefInfo.m_oldRefSegEnds',w); pk(o,*(pt(face,a_)+pt(face,b_)))
        pk(gi('WitnessRefInfo.m_refLength',w),abs(s1-s0)); struct.pack_into('<i',rec,gi('WitnessRefInfo.m_oldRefSegEndIdx',w),near)
    if os.environ.get('DIM_GEOMTAG'):
        for w in (0,1): struct.pack_into('<I',rec,gi('GeomRef.m_geomTag',w),int(os.environ['DIM_GEOMTAG']))
    if var!='noref': struct.pack_into('<Q',rec,gi('GeomRef.m_elemId',0),wA); struct.pack_into('<Q',rec,gi('GeomRef.m_elemId',1),wB)
    hdr=rep_many(T['hdr'],m); item=rep_many(T['item'],m); rec[4:12]=nid.to_bytes(8,'little')
    return bytes(hdr),g.stamp(bytes(rec)),restamp(bytes(item),8),_row(g,T,nid,8,triple)

def dim_args(A,B,half=0.22719816272965873):
    """A,B = manifest wall rows [id,x0,y0,x1,y1,...]: faces on the right-hand side of the wall direction (Revit's 'Interior' side, geometry tag 6), parallel axis-aligned walls.
    returns (axis,fa,fb,ca,cb,idA,idB) with fa<fb (face coordinates) and ca/cb the face ends (wall start, end) along the other axis"""
    def face(w):
        ux,uy=w[3]-w[1],w[4]-w[2]; L=math.hypot(ux,uy); ux,uy=ux/L,uy/L; nx,ny=uy,-ux
        return (ux,uy,w[1]+nx*half,w[2]+ny*half,w[3]+nx*half,w[4]+ny*half)
    fa,fb=face(A),face(B); vert=abs(fa[0])<1e-6 and abs(fb[0])<1e-6; horiz=abs(fa[1])<1e-6 and abs(fb[1])<1e-6
    assert vert or horiz,'dimension: walls must be parallel and axis aligned'
    if vert: ca=(fa[3],fa[5]); cb=(fb[3],fb[5]); xa,xb=fa[2],fb[2]; axis='V'
    else: ca=(fa[2],fa[4]); cb=(fb[2],fb[4]); xa,xb=fa[3],fb[3]; axis='H'
    ia,ib=A[0],B[0]
    if xa>xb: xa,xb,ca,cb,ia,ib=xb,xa,cb,ca,ib,ia
    return axis,xa,xb,ca,cb,ia,ib

# ---------------- filled regions (rectangles): 7 body records (SketchPlane, VarSketch, FilledRegion, 4 CurveElem) + 2 LinearDimString per region; template = region 0 of rosetta/<year>_view_regions_fit_var,
# every varying double fitted linearly in (x,y,w,d,x2,y2,area,perim,cx,cy) by fit_regions.py (files/regfit_<year>.json); the FilledRegion item carries a spatial key (genlib.spatial_key of the outline, 8/8 exact) at 172 ----------------
class RegionTpl:
    def __init__(self,gen,year):
        import json as _j,re as _re
        new=sorted(set(gen.e.m.ids)-set(rvtgen_ids(year))); cls={i:gen.template(i)['cls'] for i in new}
        body=[i for i in new if cls[i]!='LinearDimString']; lds=[i for i in new if cls[i]=='LinearDimString']
        self.ids=body[:7]+lds[:2]; self.T=[gen.template(i) for i in self.ids]
        self.fit=_j.load(open(os.path.expanduser('~/rvt-research/write-lab/files/regfit_%d.json'%year)))
        self.view=int(_re.search(r'(\d+)',str([v for n,o,e,v in self.T[3]['log'] if n=='Element.m_ownerDBViewId'][0])).group(1))
def rvtgen_ids(year):
    import rvtgen
    return rvtgen.Gen(os.path.expanduser('~/rvt-research/rosetta/%d_view_regions_fit_base.rte'%year)).e.m.ids
def make_region(g,RT,nids,plan_id,x,y,w,d,z,triple,z0=20.0):
    import fitgen
    feat=dict(x=x,y=y,w=w,d=d,x2=x+w,y2=y+d,one=1.0,area=w*d,perim=2*(w+d),cx=x+w/2,cy=y+d/2)
    idmap=dict(zip(RT.ids,nids)); idmap[RT.view]=plan_id; out=[]
    zb0,zb1=struct.pack('<d',z0),struct.pack('<d',z)
    for r,(T,nid) in enumerate(zip(RT.T,nids)):
        parts={}
        for key in ('hdr','rec','item'):
            b=bytearray(T[key]); fit=RT.fit.get('%d.%s'%(r,key))
            if z!=z0:                                   # level elevation first (a fitted value may legitimately equal the template z)
                k=-1
                while True:
                    k=bytes(b).find(zb0,k+1)
                    if k<0: break
                    b[k:k+8]=zb1
            if fit and fit['found']: b=fitgen.apply_fit(b,fit,feat)
            parts[key]=bytearray(rep_many(b,idmap))
        rec=parts['rec']; rec[4:12]=nid.to_bytes(8,'little'); setphase(parts['hdr']); setphase(rec); setphase(parts['item'])
        if T['cls']=='FilledRegion': parts['item'][172:176]=genlib.spatial_key((x,y,z,x+w,y+d,z))
        rec=g.stamp(bytes(rec)); row=bytearray(rep_many(T['row'],idmap)); row[0:8]=nid.to_bytes(8,'little'); struct.pack_into('<3I',row,8,*triple)
        out.append((bytes(parts['hdr']),rec,restamp(bytes(parts['item']),8),nid,bytes(row)))
    return out
