#!/usr/bin/env python3
"""rvt_write.py : build a Revit model file from a JSON scene spec with our own writer (no Revit needed).

  python3 rvt_write.py scene SPEC.json OUT.rte [--no-verify]   build, then run the offline invariants (vcheck)
  python3 rvt_write.py check SPEC.json               validate the spec only (no output)
  python3 rvt_write.py finish YEAR IN.rte OUT.rte FINISH.json [MANIFEST.json]
                                                     ONE Revit session on the offline VM (Revit-made, flagged): re-create hosted doors/windows (cuts every wall opening),
                                                     create rooms, grids, dimensions, tags, text, detail lines, filled regions, viewports. FINISH.json format: tools/finish_all.py docstring + WRITER.md;
                                                     names of walls/levels/views/sheets resolve through MANIFEST (OUT.rte.json written by `scene`)
  python3 rvt_write.py example                       print an example spec

See WRITER.md for the spec format, what each class supports and the verification protocol."""
import sys,os,json,math
WL=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,WL)

EXAMPLE={
 "year":2026,
 "levels":[{"name":"L2","elevation":12.0},{"name":"L3","elevation":24.0}],
 "params":[{"name":"Department","kind":"text"},{"name":"FireRatingMin","kind":"int"}],
 "walls":[
  {"id":"south","from":[60,0],"to":[100,0],"level":"L1","height":12.0,"mark":"W1","comments":"facade","values":{"Department":"Facade","FireRatingMin":60}},
  {"id":"east","from":[100,0],"to":[100,26],"level":"L1","height":12.0},
  {"id":"north","from":[100,26],"to":[60,26],"level":"L1","height":12.0},
  {"id":"west","from":[60,26],"to":[60,0],"level":"L1","height":12.0}],
 "floors":[{"x":60,"y":0,"width":40,"depth":26,"level":"L2"}],
 "columns":[{"x":64,"y":3,"base":"L1","top":"L2"}],
 "windows":[{"wall":"south","offset":10.0}],
 "doors":[{"wall":"south","offset":20.0}],
 "views":[{"name":"Plan L1","level":"L1"},{"name":"Plan L2","level":"L2"}],
 "sheets":[{"number":"A-101","name":"Ground floor","viewports":[{"view":"Plan L1","centre":[1.2,0.9]}]}],
 "text":[{"x":60,"y":-6,"text":"Model note"}],
 "detail_lines":[{"view":"Plan L1","from":[60,-3],"to":[100,-3]}],
 "view_text":[{"view":"Plan L1","x":62,"y":-8,"text":"View note"}],
 "filled_regions":[{"view":"Plan L1","x":62,"y":2,"w":10,"d":6}],
 "dimensions":[{"view":"Plan L3","walls":["office.west","office.east"],"at":7.0}],
 "stairs":[{"offset":[0,-80]}],
 "railings":[{"offset":[0,-80]}],
 "curtain_walls":[{"offset":[0,-90]}],
 "roofs":[{"offset":[0,-120]}],
 "topography":[{"offset":[150,-100]}],
 "roof_rects":[{"x":60,"y":-60,"width":40,"depth":26}],
 "rooms":[{"id":"office","level":"L3","x":60,"y":0,"width":20,"depth":14,"name":"Office","number":"301"}]
}
LEVEL1='L1'          # the seed's ground level (id 355, elevation 0)

class SpecError(Exception): pass

def validate(sp):
    err=[]; Y=sp.get('year')
    if Y not in (2024,2026): err.append('year must be 2024 or 2026')
    lv={LEVEL1:0.0}
    for l in sp.get('levels',[]):
        if l['name'] in lv: err.append('duplicate level %s'%l['name'])
        lv[l['name']]=float(l['elevation'])
    walls={}
    for k,w in enumerate(sp.get('walls',[])):
        if w.get('level',LEVEL1) not in lv: err.append('wall %d: unknown level %s'%(k,w.get('level')))
        if math.hypot(w['to'][0]-w['from'][0],w['to'][1]-w['from'][1])<0.5: err.append('wall %d: shorter than 0.5 ft'%k)
        if 'id' in w: walls[w['id']]=w
    pk={p['name']:p['kind'] for p in sp.get('params',[])}
    for p in sp.get('params',[]):
        if p['kind'] not in ('text','int','number','length','yesno'): err.append('param %s: kind must be text|int|number|length|yesno'%p['name'])
        if p.get('guid'):
            try: __import__('uuid').UUID(p['guid'])
            except ValueError: err.append('param %s: guid is not a GUID'%p['name'])
    for k,w in enumerate(sp.get('walls',[])):
        for n in (w.get('values') or {}):
            if n not in pk: err.append('wall %d: value for undeclared param %s'%(k,n))
    for k,f in enumerate(sp.get('floors',[])):
        if f.get('level',LEVEL1) not in lv: err.append('floor %d: unknown level'%k)
    for k,c in enumerate(sp.get('columns',[])):
        if c.get('base',LEVEL1) not in lv or c.get('top') not in lv: err.append('column %d: base/top must be known levels'%k)
        elif lv[c['top']]<=lv[c.get('base',LEVEL1)]: err.append('column %d: top level must be above base'%k)
    for kind in ('windows','doors'):
        for k,h in enumerate(sp.get(kind,[])):
            w=walls.get(h.get('wall'))
            if not w: err.append('%s %d: host wall id %r not found (give the wall an "id")'%(kind,k,h.get('wall'))); continue
            if not (abs(w['to'][1]-w['from'][1])<1e-9 and w['to'][0]>w['from'][0]): err.append('%s %d: host wall must run along +x (writer limit)'%(kind,k))
            L=w['to'][0]-w['from'][0]
            if not (1.5<=h['offset']<=L-1.5): err.append('%s %d: offset must be within the wall (1.5 ft from the ends)'%(kind,k))
            if kind=='doors' and w.get('level',LEVEL1)!=LEVEL1 and Y==2024: pass
    vn={}
    for k,v in enumerate(sp.get('views',[])):
        if v.get('level',LEVEL1) not in lv: err.append('view %d: unknown level'%k)
        vn[v['name']]=v
    placed=set()
    for s in sp.get('sheets',[]):
        for p in s.get('viewports',[]):
            if p['view'] not in vn: err.append('sheet %s: unknown view %s'%(s['number'],p['view']))
            if p['view'] in placed: err.append('view %s placed twice (Revit allows one sheet per plan view)'%p['view'])
            placed.add(p['view'])
        if len(s.get('viewports',[]))>9: err.append('sheet %s: at most 9 viewports'%s['number'])
    roomwalls={'%s.%s'%(r['id'],n) for r in sp.get('rooms',[]) if 'id' in r for n in ('south','east','north','west')}
    for k,a in enumerate(sp.get('dimensions',[])):
        if a['view'] not in vn: err.append('dimension %d: unknown view %s'%(k,a['view']))
        for n in a['walls']:
            if n not in roomwalls: err.append('dimension %d: %s is not a room wall (writer dimensions need the JOINED walls of a `rooms` entry with an "id", e.g. "office.west"; other walls: finishing pass or tools/add_dimensions.py)'%(k,n))
    for kind in ('detail_lines','view_text','filled_regions'):
        for k,a in enumerate(sp.get(kind,[])):
            if a['view'] not in vn: err.append('%s %d: unknown view %s'%(kind,k,a['view']))
    for k,gd in enumerate(sp.get('grids',[])):
        if math.hypot(gd['to'][0]-gd['from'][0],gd['to'][1]-gd['from'][1])<1: err.append('grid %d: shorter than 1 ft'%k)
    seen=set()
    for k,r in enumerate(sp.get('rooms',[])):
        lvn=r.get('level',LEVEL1)
        if lvn not in lv: err.append('room %d: unknown level %s'%(k,lvn))
        if lvn==LEVEL1: err.append('room %d: writer rooms need a level of their own (L1 already has the seed room plan); use the finishing pass for L1'%k)
        for k2,r2 in enumerate(sp.get('rooms',[])[:k]):
            if r2.get('level',LEVEL1)==lvn and r['x']<r2['x']+r2['width']+1 and r2['x']<r['x']+r['width']+1 and r['y']<r2['y']+r2['depth']+1 and r2['y']<r['y']+r['depth']+1:
                err.append('room %d: overlaps or touches (< 1 ft) room %d on the same level (writer rooms are disjoint boxes with their own walls)'%(k,k2))
        if min(r['width'],r['depth'])<3: err.append('room %d: width/depth must be >= 3 ft'%k)
    for k,rf in enumerate(sp.get('roof_rects',[])):
        if rf['width']==rf['depth']: err.append('roof_rects %d: square roofs are not supported (width != depth)'%k)
        if rf['width']<6 or rf['depth']<4: err.append('roof_rects %d: at least 6 x 4 ft'%k)
    for kind in ('stairs','railings','curtain_walls','roofs','topography','beams','wall_foundations','mep','groups'):
        for k,o in enumerate(sp.get(kind,[])):
            if len(o.get('offset',[]))!=2: err.append('%s %d: offset [dx,dy] required'%(kind,k))
    if err: raise SpecError('\n'.join(err))
    return lv

def model_centre(sp,level):
    """centre of the plan's model outline, which Revit uses to place the viewport box: extents of what the plan shows =
    elements on this level and on the level below (default view depth), the seed house (outline x 1.8..40, y 0..26) only on L1 and the level above it.
    Measured (vports1, 2026): with this rule the box lands within 0.01 ft of the requested centre."""
    lv={LEVEL1:0.0}; lv.update({l['name']:float(l['elevation']) for l in sp.get('levels',[])}); order=sorted(lv,key=lv.get); k=order.index(level)
    show={level}|({order[k-1]} if k>0 else set())
    xs=[]; ys=[]
    if LEVEL1 in show: xs+=[1.8,40.0]; ys+=[0.0,26.0]           # seed house outline as Revit measures it (vports1: L2 plan centre x 50.9)
    for w in sp.get('walls',[]):
        if w.get('level',LEVEL1) in show: xs+= [w['from'][0],w['to'][0]]; ys+=[w['from'][1],w['to'][1]]
    for f in sp.get('floors',[]):
        if f.get('level',LEVEL1) in show: xs+=[f['x'],f['x']+f['width']]; ys+=[f['y'],f['y']+f['depth']]
    if LEVEL1 in show:      # L1 objects placed by offset: Revit-made base extents (rosettas) moved by the offset; grids by their ends
        BASE={'stairs':((60,36),(75,44)),'railings':((60,50),(80,58)),'curtain_walls':((60,62),(84,62)),'roofs':((60,-100),(90,-80)),'beams':((60,70),(80,90)),'wall_foundations':((60,100),(80,100)),'mep':((60,110),(80,114)),'groups':((60,120),(70,130)),'topography':((0,0),(40,40))}
        for kind,(a,b) in BASE.items():
            for o in sp.get(kind,[]): xs+=[a[0]+o['offset'][0],b[0]+o['offset'][0]]; ys+=[a[1]+o['offset'][1],b[1]+o['offset'][1]]
        for gd in sp.get('grids',[]): xs+=[gd['from'][0],gd['to'][0]]; ys+=[gd['from'][1],gd['to'][1]]
    if not xs: return (23.5,14.0)
    return ((min(xs)+max(xs))/2,(min(ys)+max(ys))/2)

def build(sp,out):
    lvz=validate(sp); import scenes
    S=scenes.Scene(sp.get('name','spec'),sp['year']); lid={LEVEL1:355}
    for l in sp.get('levels',[]): lid[l['name']]=S.level(l['name'],float(l['elevation']))
    pid={p['name']:S.param(p['kind'],p['name'],p.get('guid')) for p in sp.get('params',[])}
    wid={}
    for w in sp.get('walls',[]):
        lv=w.get('level',LEVEL1)
        i=S.wall(tuple(w['from']),tuple(w['to']),float(w.get('height',10.0)),lid[lv],lvz[lv],mark=w.get('mark'),comments=w.get('comments'),values={pid[n]:v for n,v in (w.get('values') or {}).items()} or None)
        if 'id' in w: wid[w['id']]=(i,w)
    bylv={}
    for r in sp.get('rooms',[]): bylv.setdefault(r['level'],[]).append(r)
    for lvn,rs in bylv.items():
        res=S.rooms_level(lid[lvn],[(r['x'],r['y'],r['width'],r['depth'],r.get('name','Room'),str(r.get('number',''))) for r in rs])
        for r,(ws,rid) in zip(rs,res):
            if 'id' in r:
                for nm,wi in zip(('south','east','north','west'),ws): wid['%s.%s'%(r['id'],nm)]=(wi,None)
    for rf in sp.get('roof_rects',[]): S.roof(rf['x'],rf['y'],rf['width'],rf['depth'])
    for f in sp.get('floors',[]): S.floor(f['x'],f['y'],f['width'],f['depth'],lid[f.get('level',LEVEL1)])
    for c in sp.get('columns',[]): S.column_lv(c['x'],c['y'],lid[c.get('base',LEVEL1)],lid[c['top']])
    for kind,fn in (('windows',S.window_lv),('doors',S.door_lv)):
        for h in sp.get(kind,[]):
            i,w=wid[h['wall']]; fn(i,w['from'][0],w['from'][1],w['from'][0]+h['offset'],lid[w.get('level',LEVEL1)])
    vid={}
    for v in sp.get('views',[]): vid[v['name']]=S.planview(lid[v.get('level',LEVEL1)],v['name'])
    for s in sp.get('sheets',[]):
        sh=S.sheet(s['number'],s['name'])
        for p in s.get('viewports',[]):
            S.place(vid[p['view']],sh,tuple(p['centre']),model_centre(sp,[v for v in sp['views'] if v['name']==p['view']][0].get('level',LEVEL1)))
    for t in sp.get('text',[]): S.text(t['x'],t['y'],t['text'])
    for gd in sp.get('grids',[]): S.grid(gd['name'],tuple(gd['from']),tuple(gd['to']))
    for kind,feat in (('stairs','stair_shift'),('railings','railing_shift'),('curtain_walls','curtain_shift'),('roofs','roof_shift'),('beams','beam_shift'),('wall_foundations','wallfound_shift'),('mep','duct_shift'),('groups','group_shift')):
        for o in sp.get(kind,[]): S.shifted(feat,o['offset'][0],o['offset'][1])
    for o in sp.get('topography',[]): S.topo(o['offset'][0],o['offset'][1])
    for a in sp.get('detail_lines',[]): S.detail_line(vid[a['view']],tuple(a['from']),tuple(a['to']))
    for a in sp.get('view_text',[]): S.view_text(vid[a['view']],a['x'],a['y'],a['text'])
    for a in sp.get('dimensions',[]): S.dimension(vid[a['view']],wid[a['walls'][0]][0],wid[a['walls'][1]][0],a['at'])
    for a in sp.get('filled_regions',[]): S.filled_region(vid[a['view']],a['x'],a['y'],a['w'],a['d'])
    S.man['names']={'walls':{k:v[0] for k,v in wid.items()},'levels':{k:v for k,v in lid.items()},'views':dict(vid),'sheets':{x['number']:S.man['sheets'][i][0] for i,x in enumerate(sp.get('sheets',[]))}}
    S.commit(out); return S.counts

if __name__=='__main__':
    a=sys.argv[1:]
    if not a or a[0] in ('-h','--help'): print(__doc__); sys.exit(0)
    if a[0]=='example': print(json.dumps(EXAMPLE,indent=1)); sys.exit(0)
    if a[0]=='finish':
        import subprocess; r=subprocess.run([sys.executable,os.path.join(WL,'tools','finish_all.py')]+a[1:]); sys.exit(r.returncode)
    sp=json.load(open(a[1]))
    try:
        if a[0]=='check': validate(sp); print('spec OK'); sys.exit(0)
        if a[0]=='scene':
            c=build(sp,a[2]); print('wrote',a[2],c,'(manifest',a[2]+'.json)')
            if '--no-verify' not in a:
                import subprocess
                seed=os.path.expanduser('~/rvt-research/rosetta/%d_house_base.rte'%sp['year'])
                r=subprocess.run([sys.executable,os.path.join(WL,'vcheck.py'),a[2],'--seed',seed,'--manifest',a[2]+'.json'],capture_output=True,text=True)
                print('offline invariants:',r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:]); sys.exit(0 if 'PASS' in r.stdout else 3)
    except SpecError as e: print('SPEC ERROR:\n'+str(e)); sys.exit(2)
