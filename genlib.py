"""element makers shared by the generators (templates come from Revit-written oracle files)"""
import struct,math,zlib
def ustr(t):
    b=t.encode('utf-16le'); return struct.pack('<I',len(b)//2)+b
def rep(buf,old,new):
    k=0
    while True:
        k=buf.find(old,k)
        if k<0: return
        buf[k:k+len(old)]=new; k+=len(new)
def restamp(item,W):
    """zone/item record without its A: [id][stamp][L][tag..]: stamp-lo = Adler32 of everything after L"""
    b=bytearray(item); struct.pack_into('<I',b,W,zlib.adler32(bytes(b[W+8:]))&0xffffffff); return bytes(b)
PHASE_NEW=7019; PHASE_VISIBLE=64113   # API-made elements get 'Phase 3'; the template's views show 'Phase 1' => generated elements are created in Phase 1
def setphase(buf,W=8,old=PHASE_NEW,new=PHASE_VISIBLE): rep(buf,old.to_bytes(W,'little'),new.to_bytes(W,'little'))
def ids(T,W,nid): return T['tid'].to_bytes(W,'little'),nid.to_bytes(W,'little')
def _row(g,T,nid,W,triple):
    r=bytearray(T['row']); r[0:8]=nid.to_bytes(8,'little'); r[20:28]=nid.to_bytes(8,'little'); struct.pack_into('<3I',r,8,*triple); return bytes(r)
def hdr_ids(T,nid,W,parent_map=None):
    """new header: id at 0, self id at the end of the deletion list; parent_map {old parent id: new parent id}"""
    h=bytearray(T['hdr']); idb=nid.to_bytes(W,'little'); h[0:W]=idb
    hl={n:(o,z) for n,o,z,_ in T['hlog']}; d0,d1=hl['ElementParents.m_deletion']
    h[d1-W:d1]=idb
    for o,n in (parent_map or {}).items(): h[d0:d1-W]=bytes(h[d0:d1-W]).replace(o.to_bytes(W,'little'),n.to_bytes(W,'little'))
    return h,hl
def make_level(g,T,nid,name,z,triple):
    W=8; L={n:(o,e) for n,o,e,_ in T['log']}; idb=nid.to_bytes(W,'little')
    rec=bytearray(T['rec']); rec[4:12]=idb; rec[L['Element.m_id'][0]:L['Element.m_id'][1]]=idb
    for (n_,o,e,_) in T['log']:
        if n_=='Plane.m_origin': x,y,_z=struct.unpack_from('<3d',rec,o); struct.pack_into('<3d',rec,o,x,y,z)
    so,se=L['DatumPlane.m_text']; rec[so:se]=ustr(name)
    rec=g.stamp(bytes(rec)); hdr,_=hdr_ids(T,nid,W)
    item=bytearray(T['item']); item[0:W]=idb
    return bytes(hdr),rec,bytes(item),_row(g,T,nid,W,triple)
def make_sketchplane(g,T,nid,level_id,z,triple):
    W=8; L={n:(o,e) for n,o,e,_ in T['log']}; idb=nid.to_bytes(W,'little')
    rec=bytearray(T['rec']); rec[4:12]=idb; rec[L['Element.m_id'][0]:L['Element.m_id'][1]]=idb
    o=L['OneElementMovablePlaneRef.m_datumPlaneId'][0]; old_lv=struct.unpack_from('<Q',rec,o)[0]; struct.pack_into('<Q',rec,o,level_id)
    o=L['Trf.m_or'][0]; x,y,_=struct.unpack_from('<3d',rec,o); struct.pack_into('<3d',rec,o,x,y,z)
    # any other copy of the template's own id (Ref.m_geomRef.m_elemId) 
    rep(rec,T['tid'].to_bytes(W,'little'),idb)
    rec=g.stamp(bytes(rec)); hdr,_=hdr_ids(T,nid,W,{old_lv:level_id})
    item=bytearray(T['item']); item[0:W]=idb
    return bytes(hdr),rec,bytes(item),_row(g,T,nid,W,triple)
def make_line(g,T,nid,sp_id,p0,p1,z,triple,Tsp=None):
    W=8; L={n:(o,e) for n,o,e,_ in T['log']}; idb=nid.to_bytes(W,'little')
    zt=struct.unpack_from('<3d',T['rec'],L['GLine.m_origin'][0])[2]
    o0=struct.unpack_from('<3d',T['rec'],L['GLine.m_origin'][0]); dv=struct.unpack_from('<3d',T['rec'],L['GLine.m_dirVec'][0]); ep=struct.unpack_from('<2d',T['rec'],L['GCurve.m_endParams'][0])
    t0=struct.pack('<3d',*o0); t1=struct.pack('<3d',o0[0]+dv[0]*ep[1],o0[1]+dv[1]*ep[1],o0[2]); td=struct.pack('<3d',*dv); tl=struct.pack('<d',ep[1])
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; ln=math.hypot(dx,dy)
    rec=bytearray(T['rec']); rec[4:12]=idb; rec[L['Element.m_id'][0]:L['Element.m_id'][1]]=idb
    struct.pack_into('<Q',rec,L['CurveElem.m_sketchPlaneId'][0],sp_id)
    struct.pack_into('<2d',rec,L['GCurve.m_endParams'][0],0.0,ln)
    struct.pack_into('<3d',rec,L['GLine.m_origin'][0],p0[0],p0[1],z); struct.pack_into('<3d',rec,L['GLine.m_dirVec'][0],dx/ln,dy/ln,0.0)
    rec=g.stamp(bytes(rec))
    hdr,hl=hdr_ids(T,nid,W,{Tsp:sp_id} if Tsp else None)
    struct.pack_into('<6d',hdr,hl['Outline.m_minmax'][0],min(p0[0],p1[0]),min(p0[1],p1[1]),z,max(p0[0],p1[0]),max(p0[1],p1[1]),z)
    item=bytearray(T['item']); rep(item,T['tid'].to_bytes(W,'little'),idb)
    assert len(item)==244,len(item)
    mnx,mny,mxx,mxy=min(p0[0],p1[0]),min(p0[1],p1[1]),max(p0[0],p1[0]),max(p0[1],p1[1])
    for base in (48,96):                       # two copies of the outline (min x,y,z / max x,y,z) - found with Revit lines in 7 directions
        struct.pack_into('<3d',item,base,mnx,mny,z); struct.pack_into('<3d',item,base+24,mxx,mxy,z)
    struct.pack_into('<d',item,188,ln); struct.pack_into('<3d',item,196,p0[0],p0[1],z); struct.pack_into('<3d',item,220,dx/ln,dy/ln,0.0)
    if Tsp: rep(item,Tsp.to_bytes(W,'little'),sp_id.to_bytes(W,'little'))
    rec=bytearray(rec); hdr=bytearray(hdr); item=bytearray(item); setphase(hdr); setphase(rec); rec=g.stamp(bytes(rec)); setphase(item); item=restamp(bytes(item),W)
    return bytes(hdr),rec,bytes(item),_row(g,T,nid,W,triple)

# ---------------- walls (formulas fitted from 60 Revit walls, files/wallfit.json) ----------------
import json as _json,os as _os
_WF={}
FITYEAR=2024
def _wallfit():
    if FITYEAR not in _WF: _WF[FITYEAR]=_json.load(open(_os.path.expanduser('~/rvt-research/write-lab/files/wallfit%s.json'%('' if FITYEAR==2024 else '_26'))))
    return _WF[FITYEAR]
T2=0.32808398950131235     # half wall thickness (Generic - 200mm): 0.1 m in feet
def wall_features(x0,y0,x1,y1,h,z0):
    L=math.hypot(x1-x0,y1-y0); dx=(x1-x0)/L; dy=(y1-y0)/L
    return {'1':1.0,'x0':x0,'y0':y0,'x1':x1,'y1':y1,'dx':dx,'dy':dy,'L':L,'h':h,'z0':z0,'dxx0':dx*x0,'dxy0':dx*y0,'dyx0':dy*x0,'dyy0':dy*y0,'ang':math.atan2(dy,dx),'z1':z0+h,'xm':(x0+x1)/2,'ym':(y0+y1)/2,
            'dxxm':dx*(x0+x1)/2,'dxym':dx*(y0+y1)/2,'dyxm':dy*(x0+x1)/2,'dyym':dy*(y0+y1)/2,'L2':L/2,'h2':h/2}
def wall_bbox(x0,y0,x1,y1):
    L=math.hypot(x1-x0,y1-y0); dx=(x1-x0)/L; dy=(y1-y0)/L; nx,ny=-dy,dx
    pts=[(x0+s*nx*T2,y0+s*ny*T2) for s in (-1,1)]+[(x1+s*nx*T2,y1+s*ny*T2) for s in (-1,1)]
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; return min(xs),min(ys),max(xs),max(ys)
def apply_wall_fit(buf,key,feats,bbox):
    fit=_wallfit()[key]
    for o,(names,coef) in fit['found'].items():
        v=sum(c*feats[n] for n,c in zip(names,coef)); struct.pack_into('<d',buf,int(o),v)
    mnx,mny,mxx,mxy=bbox
    sp={'hdr':{88:mnx,96:mny,112:mxx,120:mxy},'item':{72:mnx,80:mny,96:mxx,104:mxy,120:mnx,128:mny,144:mxx,152:mxy}}.get(key,{})
    for o,v in sp.items(): struct.pack_into('<d',buf,o,v)
def _rnd(v): return math.floor(v+0.5-1e-9)
def _keyaxis(lo,hi,maxc,zero_inclusive=False):
    """smallest level l whose loose cell contains [lo,hi] (with a 1e-3 ft margin); returns (cell magnitude, negative?, level): cell = round half down of |centre|/size"""
    ctr=(lo+hi)/2; mg=0.0 if (zero_inclusive and abs(lo)<1e-9) else 1e-3      # observed: x/y boxes starting exactly at 0 pass at the cell boundary, all others need the margin
    for l in range(8):
        sz=4.0**(l+1); m=_rnd(abs(ctr)/sz); c=-m if ctr<0 else m
        if m>=maxc: continue
        if lo>=sz*(c-1)+mg-1e-9 and hi<=sz*(c+1)-mg+1e-9: return m,ctr<0,l
    raise ValueError('key out of range')
def spatial_key(bb,zero_inclusive=True):
    """Revit's per-element spatial key (loose octree cell, 4 bytes) from the element outline bb=(x0,y0,z0,x1,y1,z1) in ft. Decoded from 323 Revit walls (HANDOFF-c5-writer.md, ~98% exact):
    per axis level l (cell size 4^(l+1) ft), cell c = round(centre/size), the loose cell [size*(c-1), size*(c+1)] must contain the box (1e-3 margin); packing:
    b0 = (cx&15)<<4 | lx, b1 = (cx>>4) | (ysign<<3 | ly)<<4, b2 = |cy|, b3 = cz<<3 | lz  (cx, |cy| < 255, cz < 32; negative z centre: level + 4; negative x: untested)."""
    cx,nx,lx=_keyaxis(bb[0],bb[3],255,zero_inclusive); cy,ny,ly=_keyaxis(bb[1],bb[4],255,zero_inclusive); cz,nz,lz=_keyaxis(bb[2],bb[5],32)
    if nz: lz+=4
    if nx: lx+=8
    return bytes([((cx&15)<<4)|lx, (cx>>4)|(((8 if ny else 0)|ly)<<4), cy, (cz<<3)|lz])
def set_gtoken(item,tmpl_item,bb):
    """Revit stores that key (4 bytes) at item[316], 472, 628, 706 of a wall record: Every Revit-made wall has its own; clones of one template shared the template's and Revit's 3D picking
    (ReferenceIntersector / hover) then only found the walls whose cell matched (writer bug A, tower20)."""
    t=bytes(tmpl_item[316:320]); new=spatial_key(bb); n=0; i=-1
    while True:
        i=item.find(t,i+1)
        if i<0: break
        item[i:i+4]=new; n+=1
    assert n>=3,n
    return item
def rekey_item(item,T,hdr_new):
    """generic: replace the template's spatial key (spatial_key of the template header outline, found in the template item) by the key of the new header outline"""
    def ol(h,hlog):
        hl={x[0]:x for x in hlog}; return struct.unpack_from('<6d',h,hl['Outline.m_minmax'][1])
    try: new=spatial_key(ol(hdr_new,T['hlog']))
    except Exception: return item
    for zi in (True,False):
        try: old=spatial_key(ol(T['hdr'],T['hlog']),zi)
        except Exception: continue
        if old in T['item'] and old!=new:
            i=-1; 
            while True:
                i=item.find(old,i+1)
                if i<0: break
                item[i:i+4]=new
            return item
    return item
def make_wall(g,T,nid,level_id,p0,p1,h,z0,triple,tpl_level_id):
    """clone template wall T (a Revit wall) to a new wall from p0 to p1 with unconnected height h on level_id (elevation z0)"""
    W=8; idb=nid.to_bytes(W,'little'); feats=wall_features(p0[0],p0[1],p1[0],p1[1],h,z0); bbox=wall_bbox(p0[0],p0[1],p1[0],p1[1])
    L={n:(o,e) for n,o,e,_ in T['log']}
    rec=bytearray(T['rec']); apply_wall_fit(rec,'rec',feats,bbox); rec[4:12]=idb; rec[L['Element.m_id'][0]:L['Element.m_id'][1]]=idb
    tl=tpl_level_id.to_bytes(W,'little'); nl=level_id.to_bytes(W,'little'); rep(rec,tl,nl)
    setphase(rec); rec=g.stamp(bytes(rec))
    hdr,hl=hdr_ids(T,nid,W); apply_wall_fit(hdr,'hdr',feats,bbox); setphase(hdr)
    item=bytearray(T['item']); apply_wall_fit(item,'item',feats,bbox); rep(item,T['tid'].to_bytes(W,'little'),idb); rep(item,tl,nl); set_gtoken(item,T['item'],struct.unpack_from('<6d',hdr,hl['Outline.m_minmax'][0])); setphase(item); item=bytearray(restamp(bytes(item),W))
    return bytes(hdr),rec,bytes(item),_row(g,T,nid,W,triple)
