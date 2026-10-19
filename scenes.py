#!/usr/bin/env python3
"""scenes.py NAME OUT [YEAR] : WRITER-built scene (every added element is a clone of a Revit-made template record written by my own writer).
Seed = a Revit-made tiny house (rosetta/2024_house_base.rte) which is part of the scene (documented in the report as seed content)."""
import sys,os,struct,json,math; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL)
import rvtgen,genlib,genlib2,wledit
ROS=os.path.expanduser('~/rvt-research/rosetta')
def trip(g):
    et=g._et(); n=struct.unpack_from('<I',et,2)[0]
    best=max(range(n),key=lambda k:(struct.unpack_from('<I',et,6+40*k+12)[0],struct.unpack_from('<I',et,6+40*k+8)[0]))
    ea,eb,_=struct.unpack_from('<3I',et,6+40*best+8); return (ea,eb,eb)
SEEDF={2024:'files/ds0.rte',2026:'files/o26_line.rte'}
LVLT={2024:('files/ds3b.rte',None),2026:('files/o26_lv1.rte',None)}
WALLT={2024:('files/kwalls60.rte',301553),2026:('files/kwalls60_26.rte',303689)}
def _cached_shift_tpl(fb,fv,seed_ids):
    """GroupShiftTpl learnt from a rosetta base/var pair; pickled in ~/.cache/rvt-write (key: both files' size+mtime, seed ids, genlib2 source)"""
    import hashlib,pickle
    h=hashlib.sha1()
    for f in (fb,fv): st=os.stat(f); h.update(('%s|%d|%d|'%(f,st.st_size,st.st_mtime_ns)).encode())
    h.update(repr(sorted(seed_ids)).encode()); h.update(open(genlib2.__file__,'rb').read())
    d=os.path.expanduser('~/.cache/rvt-write'); p='%s/shift_%s.pkl'%(d,h.hexdigest())
    try:
        with open(p,'rb') as fh: return pickle.load(fh)
    except Exception: pass
    GT=genlib2.GroupShiftTpl(rvtgen.Gen(fb),rvtgen.Gen(fv),seed_ids)
    try:
        os.makedirs(d,exist_ok=True); tmp=p+'.%d'%os.getpid()
        with open(tmp,'wb') as fh: pickle.dump(GT,fh)
        os.replace(tmp,p)
    except Exception: pass
    return GT
class Scene:
    def __init__(self,name,year=2024):
        self.year=year; Y=year; suf='' if Y==2024 else '_%d'%Y; genlib2.YEAR=Y; genlib.FITYEAR=Y
        R=lambda tag: '%s/%d_%s.rte'%(ROS,Y,tag)
        self.name=name; self.g=rvtgen.Gen(os.environ['SCENE_SEED'] if os.environ.get('SCENE_SEED') else R('house_base')); g=self.g; self.tr=trip(g); self.man={}; self.reg={}; self.counts={}
        def _rows(tag): return [l.rstrip('\n').split('\t') for l in open(os.path.expanduser('~/rvt-research/gt_geom/%d_%s.tsv'%(Y,tag)),errors='replace')]
        def _ids(tag,cls,cat): return [int(r[1]) for r in _rows(tag) if r[0]=='EL' and r[2]==cls and cat in r[3]]
        hb=_ids('house_base','FamilyInstance','Structural Columns')[0], _ids('house_base','FamilyInstance','Windows')[0], _ids('house_base','FamilyInstance','Doors')[0], _ids('house_base','TextNote','')[0], _ids('house_base','Wall','')[0], _ids('house_base','Floor','')[0]
        self.T={'col':g.template(hb[0]),'win':g.template(hb[1]),'door':g.template(hb[2]),'text':g.template(hb[3])}
        self.seedtpl={'col':hb[0],'win':hb[1],'door':hb[2],'wall':hb[4],'floor':hb[5]}; self.wall_seed=hb[4]
        LT=self.T['col']['log']; self.col_sym=struct.unpack_from('<Q',self.T['col']['rec'],[o for n,o,e,_ in LT if n=='InstInfoBase.m_symbolId'][0])[0]
        gc=rvtgen.Gen(R('cols_lv_base')); gh=rvtgen.Gen(R('hosted_lv_base'))
        self.TCL=gc.template(_ids('cols_lv_base','FamilyInstance','Structural Columns')[0]); self.FCL=json.load(open(WL+'/files/colfit%s.json'%suf))
        self._R=R; self._rows_fn=_rows; self._ids_fn=_ids; self.AT=None
        self.type_copy={}
        self.WL_=None
        import collections as _co
        _wt=[gh.template(i) for i in _ids('hosted_lv_base','FamilyInstance','Windows')]
        _maj=_co.Counter(len(t['rec']) for t in _wt).most_common(1)[0][0]
        self.WL_=[t for t in _wt if len(t['rec'])==_maj][0]
        self.FWL=json.load(open(WL+'/files/winfit%s.json'%suf))
        self.DL_=gh.template(_ids('hosted_lv_base','FamilyInstance','Doors')[0]); self.FDL=json.load(open(WL+'/files/doorfit%s.json'%suf))
        # the fit explained the item outline's y (offsets 56/80/104/128) with x (the rosetta doors moved in x and y together, y = 6.67x + c):
        # Revit then drew writer doors far off their wall (house_lv: y 146..173, full scene: y 533). y = template value translated by (wall y - template y).
        _oy=struct.unpack_from('<d',self.DL_['rec'],{n:o for n,o,e,_ in self.DL_['log']}['FamilyInstance.m_instOrigin']+8)[0]
        for _o in ('56','80','104','128'):
            if _o in self.FDL['item']['found']: self.FDL['item']['found'][_o]=[['1','y'],[struct.unpack_from('<d',self.DL_['item'],int(_o))[0]-_oy,1.0]]
        LD={n:(o,e) for n,o,e,_ in self.DL_['log']}; self.dl_sym=struct.unpack_from('<Q',self.DL_['rec'],LD['InstInfoBase.m_symbolId'][0])[0]; self.dl_host=struct.unpack_from('<Q',self.DL_['rec'],LD['InsertableInst.m_hostId'][0])[0]; self.dl_lvl=struct.unpack_from('<Q',self.DL_['rec'],LD['Element.m_assocLevelId'][0])[0]
        LS2={n:(o,e) for n,o,e,_ in self.T['door']['log']}; self.door_sym=struct.unpack_from('<Q',self.T['door']['rec'],LS2['InstInfoBase.m_symbolId'][0])[0]
        LW={n:(o,e) for n,o,e,_ in self.WL_['log']}; self.wl_sym=struct.unpack_from('<Q',self.WL_['rec'],LW['InstInfoBase.m_symbolId'][0])[0]; self.wl_host=struct.unpack_from('<Q',self.WL_['rec'],LW['InsertableInst.m_hostId'][0])[0]; self.wl_lvl=struct.unpack_from('<Q',self.WL_['rec'],LW['Element.m_assocLevelId'][0])[0]
        LS={n:(o,e) for n,o,e,_ in self.T['win']['log']}; self.win_sym=struct.unpack_from('<Q',self.T['win']['rec'],LS['InstInfoBase.m_symbolId'][0])[0]
        base0=set(wledit.Editor(WL+'/'+SEEDF[Y]).m.ids)
        def _first(gx): return min(set(gx.e.m.ids)-base0)
        gpv=rvtgen.Gen(R('params_wall_var'))
        _w=[i for i in sorted(set(gpv.e.m.ids)-base0) if gpv.e.trace(i)[2]['class']=='SWall'][0]; _tw=gpv.template(_w); _LL={n:v for n,o,e,v in _tw['log']}
        import re as _re2
        genlib2.PARAM_PTR={'int':int(_re2.search(r"'ptr': (\d+)",str(_LL['Element.m_pParamValueSetInt'])).group(1)),'str':int(_re2.search(r"'ptr': (\d+)",str(_LL['Element.m_pParamValueSetAString'])).group(1))}
        print('param ptrs',genlib2.PARAM_PTR) if False else None
        self.PT=genlib2.ParamTpl(gpv,_first(gpv)); self.pkind={}; self.pname={}
        gsv=rvtgen.Gen(R('view_sheet_var')); gsb=rvtgen.Gen(R('view_sheet_base')); self.ST=genlib2.SheetTpl(gsv,_first(gsv)); self.VT=genlib2.ViewTpl(gsb,_first(gsb)); self.lvz={355:0.0}
        lf,_=LVLT[Y]; gl=rvtgen.Gen(WL+'/'+lf); self.TL=gl.template(max(gl.e.m.ids)); self.levels=[]
        gf=rvtgen.Gen(R('floors12_base')); base=set(wledit.Editor(WL+'/'+SEEDF[Y]).m.ids); allnew=sorted(set(gf.e.m.ids)-base)
        self.FT=genlib2.FloorTpl(gf,allnew[:7]+[allnew[84]])
        wf,wid=WALLT[Y]; gw=rvtgen.Gen(WL+'/'+wf); self.TW=gw.template(wid); self.wall_tpl_level=355
    def nid(self): n=self.g.nextid; self.g.nextid+=1; return n
    def _add(self,cls,key,hd,rec,it,nid,T,extra):
        self.g.new.append((hd,rec,it,nid)); self.g.rows.append(genlib._row(self.g,T,nid,8,self.tr)); self.man.setdefault(key,[]).append([nid]+extra)
        self.reg.setdefault(self.seedtpl.get(cls,0),[]).append(nid); self.counts[cls]=self.counts.get(cls,0)+1
    def column_lv(self,x,y,lv0,lv1,z1off=0.0):
        z0=self.lvz[lv0]; z1=self.lvz[lv1]+z1off; T=self.TCL; i=self.nid(); L={n:(o,e) for n,o,e,_ in T['log']}
        tb=struct.unpack_from('<Q',T['rec'],L['Element.m_assocLevelId'][0])[0]
        tt=[struct.unpack_from('<Q',T['rec'],o)[0] for n,o,e,_ in T['log'] if n=='FamilyElemRef.m_elemId'][1]
        feat={'1':1.0,'x':x,'y':y,'z0':z0,'z1':z1,'dz':z1-z0}
        sy=struct.unpack_from('<Q',T['rec'],L['InstInfoBase.m_symbolId'][0])[0]
        def ol(o,x=x,y=y,z0=z0,z1=z1,T=T,L=L):
            ox,oy=struct.unpack_from('<2d',T['rec'],L['FamilyInstance.m_instOrigin'][0]); return (x+(o[0]-ox),y+(o[1]-oy),z0,x+(o[3]-ox),y+(o[4]-oy),z1)
        hd,rec,it=genlib2.make_inst_fit(self.g,T,self.FCL,i,feat,{tb:lv0,tt:lv1,sy:self.col_sym},ol)
        rec=bytearray(rec); o=[o for n,o,e,_ in T['log'] if n=='FamilyLevelRef.m_offset'][1]; struct.pack_into('<d',rec,o,z1off); rec=self.g.stamp(bytes(rec))
        self._add('col','columns',hd,rec,it,i,T,[x,y,z0,z1,lv0]); return i
    def column(self,x,y): 
        i=self.nid(); hd,rec,it=genlib2.make_column(self.g,self.T['col'],i,x,y,0.0); self._add('col','columns',hd,rec,it,i,self.T['col'],[x,y]); return i
    def window(self,x):
        i=self.nid(); hd,rec,it=genlib2.make_hosted_x(self.g,self.T['win'],i,x); self._add('win','windows',hd,rec,it,i,self.T['win'],[x,0.0]); return i
    def door(self,x):
        i=self.nid(); hd,rec,it=genlib2.make_hosted_x(self.g,self.T['door'],i,x); self._add('door','doors',hd,rec,it,i,self.T['door'],[x,0.0]); return i
    def _load_types(self):
        if self.AT is not None: return
        R=self._R; _rows=self._rows_fn; _ids=self._ids_fn
        self.base_len={'door':len(self.T['door']['rec']),'win':len(self.T['win']['rec'])}
        ga=rvtgen.Gen(R('all_types_base')); self.GA=ga; self.AT={'door':[], 'win':[]}
        for cat,key in (('Doors','door'),('Windows','win')):
            for i in _ids('all_types_base','FamilyInstance',cat):
                t=ga.template(i)
                if len(t['rec'])!=self.base_len[key]: continue            # only the simple (non-nested) type families
                La={n:(o,e) for n,o,e,_ in t['log']}
                cp=struct.unpack_from('<Q',t['rec'],La['InstInfoBase.m_symbolId'][0])[0]; ho=struct.unpack_from('<Q',t['rec'],La['InsertableInst.m_hostId'][0])[0]
                nmr=[r[4] for r in _rows('all_types_base') if r[0]=='EL' and r[1]==str(i)][0]
                self.AT[key].append((t,ga.template(cp),cp,ho,struct.unpack_from('<Q',t['rec'],La['FamilyInstance.m_masterSymbolId'][0])[0],nmr))
    def hosted_type(self,key,k,x,host=None):
        self._load_types()
        """door/window of the k-th simple type of the seed template (7 door types, simple window types), on the seed's south wall at x"""
        t,tc,cp,ho,mid,tname=self.AT[key][k]
        if (key,k) not in self.type_copy:
            nc=self.nid(); hd,rec,it,nid,row=genlib2.make_symbol_copy(self.g,tc,nc)
            r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r)); self.type_copy[(key,k)]=nc
            self.man.setdefault('parts',[]).append([nc,'nolist'])
        nc=self.type_copy[(key,k)]; i=self.nid()
        hd,rec,it=genlib2.make_hosted_x(self.g,t,i,x,idmap={cp:nc,ho:(host or self.wall_seed)})
        self._add(key,'doors' if key=='door' else 'windows',hd,rec,it,i,t,[x,0.0,tname]); return i
    def _roomtpl(self):
        if getattr(self,'_rt',None): return self._rt
        Y=self.year; gr=rvtgen.Gen('%s/%d_rooms_lv_base.rte'%(ROS,Y)); base=set(wledit.Editor(WL+'/'+SEEDF[Y]).m.ids); new=sorted(set(gr.e.m.ids)-base)
        cls={i:gr.template(i)['cls'] for i in new}; room=[i for i in new if cls[i]=='RoomElem'][0]; plan=[i for i in new if cls[i]=='LevelRoomPlan'][0]; lvl=[i for i in new if cls[i]=='Level'][0]
        tp=gr.template(plan); ws=[]
        for n,o,e,v in tp['log']:
            if n=='RoomBoundingItem.m_linkInstOrHostId':
                w=struct.unpack_from('<Q',tp['rec'],o)[0]
                if w not in ws: ws.append(w)
        self._rt=genlib2.RoomTpl(gr,room,plan,lvl,ws[:4],self.year); return self._rt
    def room_req(self,level,x0,y0,W,D,name,number):
        """room to be created by the Revit finishing pass (tools/finish_rooms.py): the writer's own Room clone is not accepted as enclosed by Revit yet"""
        self.man.setdefault('room_requests',[]).append([level,x0+W/2,y0+D/2,name,number,W,D]); self.counts['room_req']=self.counts.get('room_req',0)+1
    def room(self,wall_ids,level,x0,y0,W,D,name,number):
        RT=self._roomtpl(); nids=(self.nid(),self.nid()); z=self.lvz.get(level,0.0)
        for hd,rec,it,nid,row in genlib2.make_room(self.g,RT,nids,wall_ids,level,x0,y0,W,D,z,name,number):
            r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r))
        self.ptopo=getattr(self,'ptopo',[])+[(level,nids[1],[nids[0]])]
        self.man.setdefault('rooms',[]).append([nids[0],name,number,level,W,D]); self.man.setdefault('parts',[]).append([nids[1],'x']); self.counts['room']=self.counts.get('room',0)+1; return nids[0]
    def rooms_level(self,level,rects):
        """N disjoint rectangular rooms on ONE level, each bounded by its own 4 joined walls: rects = [(x0,y0,W,D,name,number)]. One LevelRoomPlan for the
        level (genroom.merge of the one-room plans, circuits in reverse creation order, as Revit writes it). Returns [(wall ids, room id)]."""
        import genroom
        if getattr(self,'JT',None) is None: self.JT=genlib2.JoinRectTpl(self.year)
        n0=len(self.g.new); RT=self._roomtpl(); z=self.lvz.get(level,0.0); plan_id=self.nid(); res=[]; plans=[]; roomrows=[]; N=len(rects)
        Lr={n:(o,e) for n,o,e,_ in RT.R['log']}; cc=Lr['RoomElem.m_cachedCircuitId'][0]
        for j,(x0,y0,W,D,name,number) in enumerate(rects):
            wn=[self.nid() for _ in range(4)]
            for hd,rec,it,nid,row in genlib2.make_joined_rect(self.g,self.JT,wn,level,x0,y0,W,D,z):
                r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r))
            P=[(x0,y0),(x0+W,y0),(x0+W,y0+D),(x0,y0+D)]
            for k,i in enumerate(wn):
                self.man.setdefault('walls',[]).append([i,P[k][0],P[k][1],P[(k+1)%4][0],P[(k+1)%4][1],9.0,level,z,None,None,{}]); self.reg.setdefault(self.wall_seed,[]).append(i)
            self.counts['wall']=self.counts.get('wall',0)+4
            rid=self.nid(); outs=genlib2.make_room(self.g,RT,(rid,plan_id),wn,level,x0,y0,W,D,z,name,number)
            hd,rec,it,nid,row=outs[0]; rec=bytearray(rec); struct.pack_into('<i',rec,cc,genroom.circuit_ids(N)[j]); rec=self.g.stamp(bytes(rec)); roomrows.append((hd,rec,it,nid,row)); plans.append(outs[1])
            self.man.setdefault('rooms',[]).append([rid,name,number,level,W,D]); self.counts['room']=self.counts.get('room',0)+1; res.append((wn,rid))
        for hd,rec,it,nid,row in roomrows:
            r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r))
        # merged plan: record, header id lists = union over the one-room plans
        hd0,rec0,it0,nid0,row0=plans[0]; rec=bytearray(genroom.merge([p[1] for p in plans]))
        rec[4:12]=plan_id.to_bytes(8,'little'); rec=self.g.stamp(bytes(rec))
        hdr=hd0; hl=RT.P['hlog']
        adds={}
        for n,o,e,_ in hl:
            if n in ('ElementParents.m_deletion','ElementParents.m_regenOnly','ElementParents.m_nonDetermRegenChildren') and e-o>=4:
                ids=set()
                for p in plans:
                    h=p[0]; c=struct.unpack_from('<I',h,o)[0]; ids|={int.from_bytes(h[o+4+8*k:o+12+8*k],'little') for k in range(c)}
                adds[n]=sorted(ids)
        hdr=genlib2.hdr_list_add(hd0,hl,adds)
        r=bytearray(row0); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hdr,rec,it0,plan_id)); self.g.rows.append(bytes(r))
        z_=sorted(zip(self.g.new[n0:],self.g.rows[n0:]),key=lambda a:a[0][3]); self.g.new[n0:]=[a for a,_ in z_]; self.g.rows[n0:]=[b for _,b in z_]
        self.ptopo=getattr(self,'ptopo',[])+[(level,plan_id,[x[1] for x in res])]
        self.man.setdefault('parts',[]).append([plan_id,'x'])
        return res
    def room_box(self,level,x0,y0,W,D,name,number):
        """4 JOINED walls (9 ft, Revit-made join records fitted from rosetta rooms_lv) around (x0,y0,W,D) + a room enclosed by them, on level (id)"""
        if getattr(self,'JT',None) is None: self.JT=genlib2.JoinRectTpl(self.year)
        z=self.lvz.get(level,0.0); wn=[self.nid() for _ in range(4)]
        for hd,rec,it,nid,row in genlib2.make_joined_rect(self.g,self.JT,wn,level,x0,y0,W,D,z):
            r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r))
        P=[(x0,y0),(x0+W,y0),(x0+W,y0+D),(x0,y0+D)]
        for k,i in enumerate(wn):
            self.man.setdefault('walls',[]).append([i,P[k][0],P[k][1],P[(k+1)%4][0],P[(k+1)%4][1],9.0,level,z,None,None,{}]); self.reg.setdefault(self.wall_seed,[]).append(i)
        self.counts['wall']=self.counts.get('wall',0)+4
        return wn,self.room(wn,level,x0,y0,W,D,name,number)
    def wall_open(self,y,xs):
        """60 ft wall along +x from (0,y) at level 1 with k=len(xs) windows (first window type) that CUT the wall (fitted from rosetta/walls_open_k2)"""
        if not hasattr(self,'OW'):
            self.OW=genlib2.OpenWallTpl(rvtgen.Gen('%s/%d_walls_open_k2_base.rte'%(ROS,self.year)),'walls_open_k2_base',self.year)
        wid=self.nid(); wins=[self.nid() for _ in xs]
        for hd,rec,it,nid,row in genlib2.make_wall_open(self.g,self.OW,wid,wins,y,xs,self.tr):
            self.g.new.append((hd,rec,it,nid)); self.g.rows.append(row)
        self.man.setdefault('walls',[]).append([wid,0.0,y,60.0,y,10.0,355,0.0,None,None,{},len(xs)]); self.man.setdefault('windows',[]).extend([[w,x,y] for w,x in zip(wins,xs)])
        self.reg.setdefault(self.wall_seed,[]).append(wid); self.reg.setdefault(self.seedtpl['win'],[]).extend(wins); self.counts['wall_open']=self.counts.get('wall_open',0)+1; self.counts['win_cut']=self.counts.get('win_cut',0)+len(xs); return wid
    def door_lv(self,wall_id,wall_x0,wall_y,x,level):
        T=self.DL_; i=self.nid(); lz=self.lvz.get(level,0.0); L={n:(o,e) for n,o,e,_ in T['log']}
        oz=struct.unpack_from('<3d',T['rec'],L['FamilyInstance.m_instOrigin'][0]); ox,oy,ozz=oz
        feat={'1':1.0,'x':x,'y':wall_y,'z':lz,'hp':x-wall_x0,'lz':lz,'zr':0.0}
        def ol(o,x=x,y=wall_y,ox=ox,oy=oy,z=lz): return (o[0]+x-ox,o[1]+y-oy,o[2]-ozz+lz,o[3]+x-ox,o[4]+y-oy,o[5]-ozz+lz)
        hd,rec,it=genlib2.make_inst_fit(self.g,T,self.FDL,i,feat,{self.dl_sym:self.door_sym,self.dl_host:wall_id,self.dl_lvl:level},ol)
        self._add('door','doors',hd,rec,it,i,T,[x,wall_y]); return i
    def window_lv(self,wall_id,wall_x0,wall_y,x,level):
        """window (first window type) on a wall that runs along +x at y=wall_y starting x=wall_x0, any level (uncut); fitted from rosetta/hosted_lv"""
        T=self.WL_; i=self.nid(); lz=self.lvz.get(level,0.0); L={n:(o,e) for n,o,e,_ in T['log']}; hl={n:(o,e) for n,o,e,_ in T['hlog']}
        oz=struct.unpack_from('<3d',T['rec'],L['FamilyInstance.m_instOrigin'][0]); ox,oy=oz[0],oz[1]
        feat={'1':1.0,'x':x,'y':wall_y,'z':lz+3.0,'hp':x-wall_x0,'lz':lz,'zr':3.0}
        def ol(o,x=x,y=wall_y,ox=ox,oy=oy,z=lz): 
            return (o[0]+x-ox,o[1]+y-oy,o[2]-struct.unpack_from('<d',T['rec'],L['FamilyInstance.m_instOrigin'][0]+16)[0]+lz+3.0,o[3]+x-ox,o[4]+y-oy,o[5]-struct.unpack_from('<d',T['rec'],L['FamilyInstance.m_instOrigin'][0]+16)[0]+lz+3.0)
        hd,rec,it=genlib2.make_inst_fit(self.g,T,self.FWL,i,feat,{self.wl_sym:self.win_sym,self.wl_host:wall_id,self.wl_lvl:level},ol)
        self._add('win','windows',hd,rec,it,i,T,[x,wall_y]); return i
    def topo(self,dx,dy):
        """the rosetta 5-point 40x40 ft hill (z 0..5), translated by (dx,dy)"""
        if not hasattr(self,'TP'):
            gb=rvtgen.Gen('%s/%d_topography_shift_base.rte'%(ROS,self.year)); gv=rvtgen.Gen('%s/%d_topography_shift_var.rte'%(ROS,self.year))
            base0=set(wledit.Editor(WL+'/'+SEEDF[self.year]).m.ids); self.TP=genlib2.TopoTpl(gb,gv,min(set(gb.e.m.ids)-base0))
        i=self.nid(); hd,rec,it,nid,row=genlib2.make_topo(self.g,self.TP,i,dx,dy)
        r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r))
        self.man.setdefault('topos',[]).append([i,dx,dy]); self.counts['topo']=self.counts.get('topo',0)+1; return i
    def text(self,x,y,t):
        i=self.nid(); hd,rec,it=genlib2.make_textnote(self.g,self.T['text'],i,x,y,t); self._add('text','textnotes',hd,rec,it,i,self.T['text'],[x,y,t]); return i
    def level(self,name,z):
        i=self.nid(); self.lvz[i]=z; hd,rec,it,row=genlib.make_level(self.g,self.TL,i,name,z,self.tr); self.g.new.append((hd,rec,it,i)); self.g.rows.append(row)
        self.levels.append(i); self.man.setdefault('levels',[]).append([i,name,z]); self.counts['level']=self.counts.get('level',0)+1; return i
    def planview(self,level,name):
        nids=[self.nid() for _ in range(10)]; z=self.lvz.get(level,0.0)
        for hd,rec,it,nid,row in genlib2.make_planview(self.g,self.VT,nids,level,z,name):
            r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r))
        self.vgrp=getattr(self,'vgrp',{}); self.vgrp[nids[0]]=nids
        self.man.setdefault('views',[]).append([nids[0],name,level]); self.man.setdefault('parts',[]).extend([[i,'Viewport' if k==4 else 'x'] for k,i in enumerate(nids[1:])]); self.counts['viewplan']=self.counts.get('viewplan',0)+1; return nids[0]
    def param(self,kind,name,guid=None):
        a,b=self.nid(),self.nid()
        for hd,rec,it,nid,row in genlib2.make_param(self.g,self.PT,kind,name,a,b,guid=guid):
            r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r))
        self.pkind[a]=kind; self.pname[a]=name; self.man.setdefault('params',[]).append([a,name,kind]); self.man.setdefault('parts',[]).append([b,'x']); self.counts['param']=self.counts.get('param',0)+1; return a
    def sheet(self,number,name):
        nids=[self.nid() for _ in range(6)]
        for hd,rec,it,nid,row in genlib2.make_sheet(self.g,self.ST,nids,number,name):
            r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r))
        self.sgrp=getattr(self,'sgrp',{}); self.sgrp[nids[0]]=nids
        self.man.setdefault('sheets',[]).append([nids[0],name,number]); self.man.setdefault('parts',[]).extend([[i,'Viewport' if k==1 else 'x'] for k,i in enumerate(nids[1:])]); self.counts['sheet']=self.counts.get('sheet',0)+1; return nids[0]
    def wall(self,p0,p1,h=10.0,level=355,z0=0.0,mark=None,comments=None,values=None):
        i=self.nid(); hd,rec,it,row=genlib.make_wall(self.g,self.TW,i,level,p0,p1,h,z0,self.tr,self.wall_tpl_level)
        if values:
            sv={k:v for k,v in values.items() if self.pkind[k]=='text'}; iv={k:int(v) for k,v in values.items() if self.pkind[k] in('int','yesno')}; dv={k:float(v) for k,v in values.items() if self.pkind[k] in('number','length')}
            if comments: sv[genlib2.P_COMMENTS]=comments
            if mark: sv[genlib2.P_MARK]=mark
            rec=self.g.stamp(genlib2.add_values(rec,self.TW,strings=dict(sorted(sv.items(),key=lambda kv:kv[0]-(1<<64) if kv[0]>=1<<63 else kv[0])),ints=dict(sorted(iv.items(),key=lambda kv:kv[0]-(1<<64) if kv[0]>=1<<63 else kv[0])),doubles=dv))
            mark=comments=None
        if mark or comments:
            st={}
            if comments: st[genlib2.P_COMMENTS]=comments
            if mark: st[genlib2.P_MARK]=mark
            rec=self.g.stamp(genlib2.add_params(rec,self.TW,strings=dict(sorted(st.items(),key=lambda kv:kv[0]-(1<<64) if kv[0]>=1<<63 else kv[0]))))
        self.g.new.append((hd,rec,it,i)); self.g.rows.append(row); self.man.setdefault('walls',[]).append([i,p0[0],p0[1],p1[0],p1[1],h,level,z0,mark,comments,{self.pname[k]:v for k,v in (values or {}).items()}]); self.reg.setdefault(self.wall_seed,[]).append(i); self.counts['wall']=self.counts.get('wall',0)+1; return i
    def floor(self,x0,y0,W,D,level=355):
        nids=[self.nid() for _ in range(8)]; z=self.lvz.get(level,0.0)
        for hd,rec,it,nid,row in genlib2.make_floor(self.g,self.FT,nids,x0,y0,W,D,z,level):
            r=bytearray(row); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,nid)); self.g.rows.append(bytes(r))
        self.man.setdefault('floors',[]).append([nids[2],x0,y0,W,D,level]); self.man.setdefault('parts',[]).extend([[i] for i in nids if i!=nids[2]])
        self.reg.setdefault(self.seedtpl['floor'],[]).append(nids[2]); self.counts['floor']=self.counts.get('floor',0)+1; return nids[2]
    def place(self,plan,sheet,centre,model_centre):
        """place plan view on sheet as a viewport; centre = viewport box centre on the sheet (ft), model_centre = centre of the view's model outline (ft)"""
        if getattr(self,'VP',None) is None: self.VP=genlib2.VportTpl(rvtgen.Gen(self._R('sheet_viewport2_var' if self.year==2024 else 'sheet_viewport_var')))
        vg=self.vgrp[plan]; sg=self.sgrp[sheet]; i=self.nid(); self.vpn=getattr(self,'vpn',{}); self.vpn[sheet]=self.vpn.get(sheet,0)+1
        hd,rec,it,row=genlib2.make_viewport(self.g,self.VP,i,plan,vg[2],sheet,sg[3],centre,model_centre,str(self.vpn[sheet]))
        r=bytearray(genlib2.rep_many(row,{self.VP.draw:sg[3]})); struct.pack_into('<3I',r,8,*self.tr); self.g.new.append((hd,rec,it,i)); self.g.rows.append(bytes(r))
        self.vp_pending=getattr(self,'vp_pending',[])+[(i,plan,vg,sheet,sg)]
        self.man.setdefault('viewports',[]).append([i,'nolist',sheet,plan,list(centre)]); self.counts['viewport']=self.counts.get('viewport',0)+1; return i
    def shifted(self,feature,dx,dy):
        """translated copy of the Revit-made object of rosetta <year>_<feature>_{base,var} (stair_shift, railing_shift, curtain_shift)"""
        self.GS=getattr(self,'GS',{})
        if feature not in self.GS:
            self.GS[feature]=_cached_shift_tpl(self._R(feature+'_base'),self._R(feature+'_var'),self.g.e.m.ids)
            if self.GS[feature].unexpl and os.environ.get('RVT_WRITE_VERBOSE'): print('note',feature,'unexplained diffs',{k:v[:6] for k,v in self.GS[feature].unexpl.items()})
        GT=self.GS[feature]; self.GSD=getattr(self,'GSD',{}); reuse=self.GSD.get(feature,{})
        nids=[(reuse[i] if i in reuse else self.nid()) for i in GT.ids]
        for hd,rec,it,nid,row in genlib2.make_group_shift(self.g,GT,nids,dx,dy,self.tr,reuse): self.g.new.append((hd,rec,it,nid)); self.g.rows.append(row)
        if not reuse: self.GSD[feature]={i:n for i,n in zip(GT.ids,nids) if i in GT.shared}
        newl=[n for i,n in zip(GT.ids,nids) if i not in reuse]; self.man.setdefault('shifted',[]).append([newl[0],feature,dx,dy,newl,[i for i in GT.ids if i not in reuse]]); self.man.setdefault('parts',[]).extend([[n,'nolist'] for i,n in zip(GT.ids,nids) if i not in reuse][1:]); self.counts[feature]=self.counts.get(feature,0)+1; return nids
    def roof(self,x0,y0,W,D):
        """flat footprint roof + ceiling over the rectangle (x0,y0,W,D), level 1, W > D (clone of rosetta roof_shift, doubles from the roofs12 fit)"""
        feature='roof_shift'; self.GS=getattr(self,'GS',{})
        if feature not in self.GS: self.GS[feature]=_cached_shift_tpl(self._R(feature+'_base'),self._R(feature+'_var'),self.g.e.m.ids)
        GT=self.GS[feature]; self.GSD=getattr(self,'GSD',{}); reuse=self.GSD.get(feature,{})
        nids=[(reuse[i] if i in reuse else self.nid()) for i in GT.ids]
        for hd,rec,it,nid,row in genlib2.make_roof_group(self.g,GT,nids,x0,y0,W,D,self.tr,reuse,self.year): self.g.new.append((hd,rec,it,nid)); self.g.rows.append(row)
        if not reuse: self.GSD[feature]={i:n for i,n in zip(GT.ids,nids) if i in GT.shared}
        newl=[n for i,n in zip(GT.ids,nids) if i not in reuse]
        self.man.setdefault('roofs',[]).append([nids[GT.ids.index(genlib2.ROOF_FIRST[self.year])],x0,y0,W,D]); self.man.setdefault('parts',[]).extend([[n,'nolist'] for n in newl]); self.counts['roof']=self.counts.get('roof',0)+1; return nids
    def grid(self,name,p0,p1):
        if getattr(self,'GT_',None) is None: self.GT_=genlib2.grid_template(rvtgen.Gen(self._R('grid_level_base')))
        i=self.nid(); hd,rec,it,row=genlib2.make_grid(self.g,self.GT_,i,name,p0,p1,self.tr); self.g.new.append((hd,rec,it,i)); self.g.rows.append(row)
        self.man.setdefault('grids',[]).append([i,name,list(p0),list(p1)]); self.counts['grid']=self.counts.get('grid',0)+1; return i
    def _anno(self):
        if getattr(self,'ATn',None) is None: self.ATn=genlib2.AnnoTpl(rvtgen.Gen(self._R('view_k_annotations_var')))
        return self.ATn
    def detail_line(self,plan,p0,p1):
        AT=self._anno(); vg=self.vgrp[plan]; lv=[v for v in self.man['views'] if v[0]==plan][0][2]; z=self.lvz.get(lv,0.0); i=self.nid()
        hd,rec,it,row=genlib2.make_detail_line(self.g,AT,i,plan,vg[8],p0,p1,z,self.tr); self.g.new.append((hd,rec,it,i)); self.g.rows.append(row)
        self.man.setdefault('detail_lines',[]).append([i,'nolist',plan,list(p0),list(p1)]); self.counts['detail_line']=self.counts.get('detail_line',0)+1; return i
    def view_text(self,plan,x,y,t):
        AT=self._anno(); lv=[v for v in self.man['views'] if v[0]==plan][0][2]; z=self.lvz.get(lv,0.0); i=self.nid()
        hd,rec,it=genlib2.make_view_text(self.g,AT,i,plan,x,y,z,t); self.g.new.append((hd,rec,it,i)); self.g.rows.append(genlib._row(self.g,AT.T['text'],i,8,self.tr))
        self.man.setdefault('view_texts',[]).append([i,'nolist',plan,x,y,t]); self.counts['view_text']=self.counts.get('view_text',0)+1; return i
    def dimension(self,plan,wall_a,wall_b,c,half=0.22719816272965873):
        """linear dimension in plan view `plan` between the faces (tag 6 = right-hand side of the wall direction) of two parallel axis-aligned walls of the manifest, dimension line at
        coordinate c. EXPERIMENTAL: Revit rejects the file (InternalException on open) unless the two walls were already regenerated by Revit (see HANDOFF-c5-writer.md)."""
        W={w[0]:w for w in self.man['walls']}; axis,xa,xb,ca,cb,wall_a,wall_b=genlib2.dim_args(W[wall_a],W[wall_b],half)
        DT=getattr(self,'DTn',None)
        if DT is None: DT=self.DTn=genlib2.DimTpl(rvtgen.Gen(self._R('view_dims_fit_var')))
        lv=[v for v in self.man['views'] if v[0]==plan][0][2]; z=self.lvz.get(lv,0.0); i=self.nid()
        hd,rec,it,row=genlib2.make_dimension(self.g,DT,i,plan,wall_a,wall_b,axis,xa,xb,ca,cb,c,z,self.tr); self.g.new.append((hd,rec,it,i)); self.g.rows.append(row)
        self.man.setdefault('dimensions',[]).append([i,'nolist',plan,wall_a,wall_b,axis,xa,xb,c,abs(xb-xa)]); self.counts['dimension']=self.counts.get('dimension',0)+1; return i
    def filled_region(self,plan,x,y,w,d):
        """rectangular filled region in plan view `plan` (writer-built: 7 records + 2 sketch dimensions, rosetta view_regions_fit fitted)"""
        RT=getattr(self,'RTn',None)
        if RT is None: RT=self.RTn=genlib2.RegionTpl(rvtgen.Gen(self._R('view_regions_fit_var')),self.year)
        lv=[v for v in self.man['views'] if v[0]==plan][0][2]; z=self.lvz.get(lv,0.0); nids=[self.nid() for _ in RT.ids]
        for hd,rec,it,nid,row in genlib2.make_region(self.g,RT,nids,plan,x,y,w,d,z,self.tr): self.g.new.append((hd,rec,it,nid)); self.g.rows.append(row)
        self.man.setdefault('filled_regions',[]).append([nids[2],'nolist',plan,x,y,w,d]); self.man.setdefault('parts',[]).extend([[n,'nolist'] for n in nids if n!=nids[2]]); self.counts['filled_region']=self.counts.get('filled_region',0)+1; return nids[2]
    def _apply_viewports(self):
        g=self.g; idx={e[3]:k for k,e in enumerate(g.new)}; VT=self.VT.T; ST=self.ST.T
        hadd={}; dadd={}
        for vp,plan,vg,sheet,sg in getattr(self,'vp_pending',[]):
            hadd.setdefault(plan,(VT[0],{}))[1].setdefault('ElementParents.m_regenOnly',[]).append(sheet)
            hadd.setdefault(vg[2],(VT[2],{}))[1].setdefault('ElementParents.m_regenOnly',[]).extend([sheet,vp])
            hadd.setdefault(sheet,(ST[0],{}))[1].setdefault('ElementParents.m_regenOnly',[]).extend([plan,vp])
            hadd.setdefault(sg[3],(ST[3],{}))[1].setdefault('ElementParents.m_deletion',[]).append(vp)
            dadd.setdefault(sg[3],[]).append(vp)
            # plan record: DBView.m_sheetViewportElemId (shifted by the name length change)
            k=idx[plan]; hd,rec,it,nid=g.new[k]; T=VT[0]; L={n:(o,e) for n,o,e,_ in T['log']}
            o=L['DBView.m_sheetViewportElemId'][0]; o+= (len(rec)-len(T['rec'])) if o>=L['DBView.m_viewName'][1] else 0
            r=bytearray(rec); assert r[o:o+8]==b'\xff'*8; r[o:o+8]=vp.to_bytes(8,'little'); g.new[k]=(hd,g.stamp(bytes(r)),it,nid)
        for nid,(T,adds) in hadd.items():
            k=idx[nid]; hd,rec,it,_=g.new[k]; g.new[k]=(genlib2.hdr_list_add(hd,T['hlog'],adds),rec,it,nid)
        for nid,vps in dadd.items():
            k=idx[nid]; hd,rec,it,_=g.new[k]; T=ST[3]; o,e=[(o,e) for n,o,e,_ in T['log'] if n=='DBDrawing.m_viewports'][0]
            r=bytearray(rec); n=struct.unpack_from('<I',r,o)[0]; cur=[int.from_bytes(r[o+4+8*j:o+12+8*j],'little') for j in range(n)]
            lst=cur+vps; r[o:o+4+8*n]=struct.pack('<I',len(lst))+b''.join(v.to_bytes(8,'little') for v in lst); g.new[k]=(hd,g.stamp(bytes(r)),it,nid)
    def _apply_plan_topologies(self):
        """register every writer room's level, LevelRoomPlan and room in the document's AllPlanTopologies element (Revit's index of the
        per-level room topologies). Without it Revit never finds the writer's LevelRoomPlan: rooms open with area 0 (2026-10-15)."""
        pts=getattr(self,'ptopo',[])
        if not pts: return
        g=self.g; apt=441 if g.e.trace(441)[2]['class']=='AllPlanTopologies' else [i for i in sorted(g.e.m.ids) if i<301553 and g.e.trace(i)[2]['class']=='AllPlanTopologies'][0]; T=g.template(apt)
        L=[(n,o,e) for n,o,e,_ in T['log']]; s0,s1=[(o,e) for n,o,e in L if n=='PlanTopologies.m_set'][0]
        f={n:(o,e) for n,o,e in L if n.startswith('PlanTopology.')}      # fields of the (last) existing entry
        e0=f['PlanTopology.m_elevOffset'][0]; e1=max(e for o,e in f.values()); assert e1==s1,'entry layout'
        tpl=T['rec'][e0:e1]; rel=lambda n: f[n][0]-e0
        rec=bytearray(T['rec']); n=struct.unpack_from('<I',rec,s0)[0]; ents=b''
        for lv,plan,room in pts:
            ent=bytearray(tpl); ent[rel('PlanTopology.m_levelId'):rel('PlanTopology.m_levelId')+8]=lv.to_bytes(8,'little')
            ent[rel('PlanTopology.m_levelRoomPlanId'):rel('PlanTopology.m_levelRoomPlanId')+8]=plan.to_bytes(8,'little')
            struct.pack_into('<I',ent,rel('PlanTopology.m_nextCircuitId'),2*len(room)); ents+=bytes(ent)
        rec[s1:s1]=ents; struct.pack_into('<I',rec,s0,n+len(pts))
        hdr=genlib2.hdr_list_add(T['hdr'],T['hlog'],{'ElementParents.m_deletion':[x for lv,pl,_ in pts for x in (lv,pl)],
            'ElementParents.m_regenOnly':[x for _,_,r in pts for x in r],'ElementParents.m_nonDetermRegenChildren':[x for _,_,r in pts for x in r]})
        g.replace_existing(apt,hdr=hdr,rec=bytes(rec)); self.man.setdefault('edited',[]).append(apt)
    def _rephase_seed(self):
        """The seed house was made through the API in 'Phase 3' while the template's own views (and the 3D view Revit's GUI creates) show 'Phase 1': there every Phase 3 element
        does not exist yet, so the seed walls/doors/windows/columns/floor/room vanished in the GUI 3D view while the writer's Phase 1 elements showed (user bug B). Move the seed's phase-aware
        elements to Phase 1 like the writer's own (rec created phase + the phase parent in the header)."""
        g=self.g; moved=[]
        rows=[l.rstrip('\n').split('\t') for l in open(os.path.expanduser('~/rvt-research/gt_geom/%d_house_base.tsv'%self.year),errors='replace')]
        for r in rows:
            if r[0]!='EL' or r[2] not in ('Wall','FamilyInstance','Floor','Room'): continue
            i=int(r[1]); t=g.template(i); o=[o for n,o,e,_ in t['log'] if n=='Element.m_createdPhaseId']
            if not o or struct.unpack_from('<Q',t['rec'],o[0])[0]!=genlib.PHASE_NEW: continue
            rec=bytearray(t['rec']); struct.pack_into('<Q',rec,o[0],genlib.PHASE_VISIBLE); hdr=bytearray(t['hdr']); genlib.setphase(hdr)
            g.replace_existing(i,hdr=bytes(hdr),rec=bytes(rec)); moved.append(i)
        if moved: self.man.setdefault('edited',[]).extend(moved); self.man['rephased']=moved
    def commit(self,out):
        self._rephase_seed()
        self._apply_viewports(); self._apply_plan_topologies()
        g=self.g; known=set(g.e.m.ids)
        def comp(raw):
            ops=genlib2.registry_update(raw,{k:v for k,v in self.reg.items() if k},known)
            if self.levels:
                from gen_levels import latest_patch
                ops+=latest_patch(raw,list(self.levels),self.year,as_ops=True,O=genlib2.level_offsets(raw,self.year))
            rs=sorted((o[0],o[0]+o[1]) for o in ops)
            assert all(rs[i][1]<=rs[i+1][0] for i in range(len(rs)-1)),'overlapping Latest ops'
            raw=genlib2.apply_ops(raw,ops)
            if self.man.get('grids') and not os.environ.get('GRID_NOREG'): raw=genlib2.set_last_grid_name(genlib2.grid_registry(raw,genlib2.grid_anchors(self.year),[r[0] for r in self.man['grids']]),self.man['grids'][-1][1])
            return raw
        g.latest_edits=[('Latest',comp)]; g.itag=self.T['text']['item'][16:18]; g.commit(out)
        json.dump(self.man,open(out+'.json','w')); json.dump(dict(scene=self.name,counts=self.counts,seed='rosetta/2024_house_base.rte (Revit-made: 5 walls, 2 doors, 3 windows, 2 columns, floor, room, tag, text)'),open(out+'.report.json','w'),indent=1)
def house2(S):
    house1(S)
    ls=[S.level(nm,z) for nm,z in (('Writer L2',12.0),('Writer L3',24.0),('Writer Roof',36.0))]
    for lv,z in zip(ls[:2],(12.0,24.0)):
        for (a,b) in (((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0))): S.wall(a,b,12.0,lv,z)
def frame1(S):
    ls=[355]+[S.level('Writer L%d'%(k+2),12.0*(k+1)) for k in range(4)]
    for k in range(4):
        for (a,b) in (((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0))): S.wall(a,b,12.0,ls[k],12.0*k)
        S.floor(60,0,40,26,ls[k])
        for i in range(3):
            for j in range(3): S.column_lv(64+i*16.0,3+j*10.0,ls[k],ls[k+1])
def views1(S):
    ls=[S.level('View L%d'%(k+2),12.0*(k+1)) for k in range(3)]
    for k,l in enumerate(ls): S.planview(l,'Writer plan %d'%(k+2))
def params1(S):
    for k,(a,b) in enumerate((((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0)))): S.wall(a,b,10.0,mark='W-%02d'%(k+1),comments='writer wall %d: exterior'%(k+1))
def storeys(S,n,h=12.0,prefix='L'):
    return [355]+[S.level('%s%d'%(prefix,k+2),h*(k+1)) for k in range(n)]
def building(S,ls,x0,y0,W,D,n,h=12.0,core=True,cx=3,cy=3,tag='B',views=False,pv=None,win=0):
    for k in range(n):
        lv=ls[k]; z=h*k
        wl=[S.wall(a,b,h,lv,z,mark='%s%d-EW'%(tag,k+1),comments='%s storey %d exterior wall'%(tag,k+1),values=(pv(k,True) if pv else None)) for a,b in (((x0,y0),(x0+W,y0)),((x0+W,y0),(x0+W,y0+D)),((x0+W,y0+D),(x0,y0+D)),((x0,y0+D),(x0,y0)))]
        for j in range(win): S.window_lv(wl[0],x0,y0,x0+W*(j+1)/(win+1),lv)
        if core:
            cw,cd=W*0.3,D*0.3; ccx,ccy=x0+W/2-cw/2,y0+D/2-cd/2
            for a,b in (((ccx,ccy),(ccx+cw,ccy)),((ccx+cw,ccy),(ccx+cw,ccy+cd)),((ccx+cw,ccy+cd),(ccx,ccy+cd)),((ccx,ccy+cd),(ccx,ccy))): S.wall(a,b,h,lv,z,mark='%s%d-CORE'%(tag,k+1),comments='core wall',values=(pv(k,False) if pv else None))
        S.floor(x0,y0,W,D,lv)
        for i in range(cx):
            for j in range(cy): S.column_lv(x0+W*(i+0.5)/cx,y0+D*(j+0.5)/cy,lv,ls[k+1])
def office5(S):
    ls=storeys(S,5); building(S,ls,60,0,60,36,5,tag='O')
    for k in range(1,6): S.planview(ls[k],'Office plan L%d'%(k+1))
    S.text(60,-6,'Office block - writer-built (5 storeys)')
def tower20(S):
    ls=storeys(S,20,12.0,'T'); building(S,ls,60,0,40,40,20,12.0,True,4,4,'T')
    for k in (1,5,10,15,20): S.planview(ls[k],'Tower plan %d'%(k+1))
def campus3(S):
    ls=storeys(S,6)
    building(S,ls,60,0,50,30,4,tag='A'); building(S,ls,140,0,40,40,6,tag='B'); building(S,ls,60,70,70,24,3,tag='C',core=False,cx=4,cy=2)
    for k in range(1,7): S.planview(ls[k],'Campus plan L%d'%(k+1))
    S.text(60,-6,'Campus: blocks A (4), B (6), C (3 storeys)')
def sheets1(S):
    for k in range(3): S.sheet('W-%d00'%(k+1),'Writer sheet %d'%(k+1))
def params2(S):
    pt=S.param('text','RosText'); pi=S.param('int','RosInt'); pn=S.param('number','RosNum'); pl=S.param('length','RosLen'); py=S.param('yesno','RosYN')
    for k,(a,b) in enumerate((((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0)))): S.wall(a,b,10.0,mark='P-%02d'%(k+1),comments='param wall %d'%(k+1),values={pt:'alpha%d'%k,pi:7+k,pn:2.5+k,pl:12.0+k,py:k%2})
def _pk(kind,val):
    def f(S):
        pid=S.param(kind,'Ros'+kind.capitalize())
        S.wall((60,0),(100,0),10.0,mark='PK',values={pid:val})
    return f
def campus4(S):
    campus3(S)
    for k in range(4): S.sheet('A-%d01'%(k+1),'Campus sheet %d'%(k+1))
def office6(S):
    pd=S.param('text','Department'); pf=S.param('int','FireRatingMin'); pu=S.param('number','UValue'); pl=S.param('length','ThermalDepth'); pb=S.param('yesno','LoadBearing')
    def pv(k,ext): return {pd:('Facade' if ext else 'Core'),pf:(60 if ext else 120),pu:(0.28 if ext else 0.0),pl:(0.75 if ext else 0.5),pb:int(not ext)}
    ls=storeys(S,5); building(S,ls,60,0,60,36,5,tag='O',pv=pv)
    for k in range(1,6): S.planview(ls[k],'Office plan L%d'%(k+1))
    for k in range(5): S.sheet('O-%d01'%(k+1),'Office sheet L%d'%(k+1))
    S.text(60,-6,'Office block with shared parameters, views and sheets - writer-built')
def types1(S):
    S._load_types()
    for k in range(len(S.AT['door'])): S.hosted_type('door',k,4.0+k*4.5)
    nw=min(len(S.AT['win']),8)
    for k in range(nw): S.hosted_type('win',k,6.25+k*4.5)
def rooms1(S):
    ls=[S.level('Room L%d'%(k+2),12.0*(k+1)) for k in range(3)]
    for k,lv in enumerate(ls):
        x0,y0,W,D=60+5*k,5,20+4*k,14; z=12.0*(k+1)
        ws=[S.wall(a,b,9.0,lv,z) for a,b in (((x0,y0),(x0+W,y0)),((x0+W,y0),(x0+W,y0+D)),((x0+W,y0+D),(x0,y0+D)),((x0,y0+D),(x0,y0)))]
        S.room(ws,lv,x0,y0,W,D,'Writer room %d'%(k+1),str(100+k))
def roombox1(S):
    for k in range(3):
        lv=S.level('RB L%d'%(k+2),12.0*(k+1)); S.room_box(lv,60+5*k,5,20+4*k,14,'Box room %d'%(k+1),str(200+k))
def open1(S):
    for i,xs in enumerate(([20.0],[10.0,40.0],[8.0,26.0,47.0],[6.0,20.0,34.0,50.0])): S.wall_open(120.0+30*i,xs)
def fitout1(S):
    types1(S)
    pd=S.param('text','Department'); pf=S.param('int','FireRatingMin')
    ls=[S.level('Fitout L%d'%(k+2),12.0*(k+1)) for k in range(3)]
    for k,lv in enumerate(ls):
        x0,y0,W,D=60+5*k,5,20+4*k,14; z=12.0*(k+1)
        ws=[S.wall(a,b,9.0,lv,z,mark='F%d-%d'%(k+1,j+1),comments='fit-out partition',values={pd:('Reception','Offices','Meeting')[k],pf:30*(k+1)}) for j,(a,b) in enumerate((((x0,y0),(x0+W,y0)),((x0+W,y0),(x0+W,y0+D)),((x0+W,y0+D),(x0,y0+D)),((x0,y0+D),(x0,y0))))]
        S.room_req(lv,x0,y0,W,D,('Reception','Offices','Meeting room')[k],str(200+k)); S.planview(lv,'Fit-out plan %d'%(k+1))
    for k in range(3): S.sheet('F-%d01'%(k+1),'Fit-out sheet %d'%(k+1))
    S.text(60,-4,'Fit-out: door/window types, rooms, shared parameters - writer-built')
def open2(S):
    S.wall_open(140.0,[11.4,24.35,35.27,49.52]); S.wall_open(215.0,[11.4,24.35,35.27,49.52]); S.wall_open(262.0,[12.4,25.35,36.27,50.52]); S.wall_open(295.0,[8.0,24.0,38.0,52.0])
    S.wall_open(335.0,[30.0]); S.wall_open(355.0,[10.0,30.0]); S.wall_open(375.0,[10.0,30.0,50.0])
def office7(S):
    pd=S.param('text','Department'); pf=S.param('int','FireRatingMin'); pu=S.param('number','UValue'); pl=S.param('length','ThermalDepth'); pb=S.param('yesno','LoadBearing')
    def pv(k,ext): return {pd:('Facade' if ext else 'Core'),pf:(60 if ext else 120),pu:(0.28 if ext else 0.0),pl:(0.75 if ext else 0.5),pb:int(not ext)}
    ls=storeys(S,5); building(S,ls,60,0,60,36,5,tag='O',pv=pv,win=5)
    for k in range(1,6): S.planview(ls[k],'Office plan L%d'%(k+1))
    for k in range(5): S.sheet('O-%d01'%(k+1),'Office sheet L%d'%(k+1))
    S.text(60,-6,'Office block: shared parameters, 25 windows on the south facade, views, sheets - writer-built')
def open3(S):
    import random
    rnd=random.Random(5); y=0.0
    for k in (1,2,3,4):
        for rep in range(8):
            xs=[]
            while len(xs)<k:
                x=round(4+rnd.random()*52,2)
                if all(abs(q-x)>=8 for q in xs): xs.append(x)
            if 250.0<y<260.0: y=260.0
            S.wall_open(y,sorted(xs)); y+=14.0
def house_lv(S):
    ls=[355]+[S.level('Writer L2',12.0)]
    w=[S.wall(a,b,10.0,355,0.0,mark='B-%d'%(k+1),comments='block B wall') for k,(a,b) in enumerate((((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0))))]
    S.floor(60,0,40,26,355)
    for i in range(5):
        for j in range(3): S.column_lv(64+i*8.0,3+j*10.0,355,ls[1])
    for k in range(6): S.window_lv(S.wall_seed,0.0,0.0,14+k*2.5,355)
    S.door_lv(S.wall_seed,0.0,0.0,32.0,355); S.door_lv(S.wall_seed,0.0,0.0,35.5,355)
    S.planview(ls[1],'Writer plan 2'); S.text(62,-4,'Block B - writer-built (house_lv)')
def _hl(win,door,view,text):
    def f(S):
        ls=[355]+[S.level('Writer L2',12.0)]
        for k,(a,b) in enumerate((((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0)))): S.wall(a,b,10.0,355,0.0)
        S.floor(60,0,40,26,355)
        for i in range(2): S.column_lv(64+i*8.0,3.0,355,ls[1])
        if win:
            for k in range(2): S.window_lv(S.wall_seed,0.0,0.0,14+k*2.5,355)
        if door: S.door_lv(S.wall_seed,0.0,0.0,32.0,355)
        if view: S.planview(ls[1],'Writer plan 2')
        if text: S.text(62,-4,'bisect')
    return f
def topo1(S):
    for k,(dx,dy) in enumerate(((-100,-100),(-100,0),(-100,100),(150,-100),(150,60))): S.topo(dx,dy)
def campus5(S):
    campus4(S)
    for dx,dy in ((0,-70),(60,-70),(120,-70),(180,-70),(-10,-70)): S.topo(dx,dy)
    S.text(60,-80,'Campus with topography (5 hill patches), 3 buildings, 6 plan views, 4 sheets - writer-built')
def house1(S):
    for (a,b) in (((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0))): S.wall(a,b)
    S.floor(60,0,40,26)
    top=S.level('Writer Top',13.123359580052492)
    for i in range(5):
        for j in range(3): S.column_lv(64+i*8.0,3+j*10.0,355,top)      # fitted column (the old single-template column() left Revit's geometry cache at the template position: 3D pick missed it)
    for k in range(6): S.window(14+k*2.5)
    S.door(32.0); S.door(35.5)
    S.text(62,-4,'Block B - writer-built (house1)'); S.text(2,-4,'Block A - Revit-made seed house')
def vports1(S):
    ls=storeys(S,3); 
    for (a,b) in (((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0))): S.wall(a,b,10.0,ls[1],12.0)
    for k in range(1,3):
        v=S.planview(ls[k],'VP plan %d'%(k+1)); sh=S.sheet('P-%d01'%k,'Viewport sheet %d'%k); S.place(v,sh,(1.2,0.9),(50.0,13.0))
def anno1(S):
    ls=storeys(S,2)
    for (a,b) in (((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0))): S.wall(a,b,10.0,ls[1],12.0)
    v=S.planview(ls[1],'Anno plan 2')
    for k in range(4): S.detail_line(v,(62+k*8,2),(66+k*8,24))
    S.detail_line(v,(60,-3),(100,-3))
    S.view_text(v,62,-6,'Writer view note A'); S.view_text(v,80,30,'Second note, longer text')
    sh=S.sheet('N-101','Annotated plan'); S.place(v,sh,(1.2,0.9),(80.0,13.0))
def dims1(S):
    ls=storeys(S,2); w=[S.wall(a,b,10.0,ls[1],12.0) for (a,b) in (((60,0),(100,0)),((100,0),(100,26)),((100,26),(60,26)),((60,26),(60,0)))]
    v=S.planview(ls[1],'Dims plan 2')
    S.dimension(v,w[3],w[1],13.0); S.dimension(v,w[3],w[1],5.0); S.dimension(v,w[0],w[2],80.0); S.dimension(v,w[0],w[2],70.0)
    sh=S.sheet('D-101','Dimensioned plan'); S.place(v,sh,(1.2,0.9),(80.0,13.0))
def dims2(S):
    lv=S.level('DM L2',12.0); wn,_=S.room_box(lv,60,5,20,14,'Dim room','301'); v=S.planview(lv,'Dim plan 2')
    S.dimension(v,wn[3],wn[1],12.0); S.dimension(v,wn[3],wn[1],8.0); S.dimension(v,wn[0],wn[2],70.0)
    sh=S.sheet('D-102','Dimensioned room'); S.place(v,sh,(1.2,0.9),(70.0,12.0))
def regions1(S):
    ls=storeys(S,2); S.wall((60,0),(100,0),10.0,ls[1],12.0); v=S.planview(ls[1],'Regions plan 2')
    for (x,y,w,d) in ((62,2,10,6),(75,3,4,12),(84,10,12,3),(66,14,6,6)): S.filled_region(v,x,y,w,d)
    sh=S.sheet('R-101','Filled regions'); S.place(v,sh,(1.2,0.9),(80.0,13.0))
def office8(S):
    office6(S)
    for k,((v,_,_),(sh,_,_)) in enumerate(zip(S.man['views'],S.man['sheets'])): S.place(v,sh,(1.4,1.0),((1.8+120)/2 if k==0 else 90.0,18.0))
    for k,(v,_,_) in enumerate(S.man['views']):
        S.detail_line(v,(60,-3),(120,-3)); S.view_text(v,60,-5,'Level %d plan - writer-built viewport and annotations'%(k+2))
def grids1(S):
    for k in range(5): S.grid('W%d'%(k+1),(60+10*k,-10),(60+10*k,40))
    for k,l in enumerate('ABC'): S.grid(l,(55,13*k),(110,13*k))
    S.grid('D1',(55,-5),(110,35))
def roofs2(S):
    S.shifted('roof_shift',0,0); S.shifted('roof_shift',40,0); S.shifted('roof_shift',0,40)
def shift1(S):
    S.shifted('stair_shift',0,0); S.shifted('stair_shift',30,0)
    S.shifted('railing_shift',0,0); S.shifted('railing_shift',0,20)
    S.shifted('curtain_shift',0,0); S.shifted('curtain_shift',0,30)
def grid1(S): S.grid('W1',(60,-10),(60,40))
def grid1b(S): S.grid('G2',(10,-5),(10,25))
def grid1c(S): S.grid('W1',(10,-5),(10,25))
def grid1d(S): S.grid('G2',(60,-10),(60,40))
LADDER={'regions1':regions1,'dims2':dims2,'dims1':dims1,'roombox1':roombox1,'roofs2':roofs2,'grid1':grid1,'grid1b':grid1b,'grid1c':grid1c,'grid1d':grid1d,'shift1':shift1,'grids1':grids1,'anno1':anno1,'vports1':vports1,'office8':office8,'campus5':campus5,'topo1':topo1,'hlBC':_hl(1,1,0,0),'hlBCDE':_hl(1,1,1,1),'hlBDE':_hl(1,0,1,1),'hlCDE':_hl(0,1,1,1),'hlB':_hl(1,0,0,0),'hlC':_hl(0,1,0,0),'hlD':_hl(0,0,1,0),'hlE':_hl(0,0,0,1),'house_lv':house_lv,'open3':open3,'office7':office7,'open2':open2,'fitout1':fitout1,'open1':open1,'rooms1':rooms1,'types1':types1,'office6':office6,'campus4':campus4,'pk_int':_pk('int',7),'pk_number':_pk('number',2.5),'pk_length':_pk('length',12.0),'pk_yesno':_pk('yesno',1),'pk_text':_pk('text','abc'),'params2':params2,'sheets1':sheets1,'office5':office5,'tower20':tower20,'campus3':campus3,'params1':params1,'views1':views1,'house1':house1,'house2':house2,'frame1':frame1}
if __name__=='__main__':
    S=Scene(sys.argv[1],int(sys.argv[3]) if len(sys.argv)>3 else 2024); LADDER[sys.argv[1]](S); S.commit(sys.argv[2]); print('wrote',sys.argv[2],S.counts)
