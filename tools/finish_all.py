#!/usr/bin/env python3
"""finish_all.py YEAR IN OUT FINISH.json [MANIFEST.json] : ONE Revit session, Revit-made finishing of a writer file (flagged: these elements are made by the Revit API, everything else stays writer output).
FINISH.json (names resolve through MANIFEST 'names': walls/levels/views/sheets; numbers are raw element ids):
 {"openings": true,                                   re-create every hosted door/window (opens the walls, any geometry)
  "touch_walls": true,                                 nudge every wall + regenerate (refreshes the level plan topology; implied by rooms)
  "rooms":   [{"level":"L1","x":10,"y":8,"name":"Hall","number":"101"}],
  "grids":   [{"name":"A","from":[0,0],"to":[0,40]}],
  "dimensions":[{"view":"Plan L1","walls":["south","north"],"offset":3.0}  |  {"view":..,"grids":["A","B"],"offset":3.0}],
  "tags":    [{"view":"Plan L1","element":<id or wall/door name>,"at":[x,y]}],
  "text":    [{"view":"Plan L1","x":1,"y":2,"text":"..."}],
  "detail_lines":[{"view":"Plan L1","from":[0,0],"to":[5,0]}],
  "filled_regions":[{"view":"Plan L1","x":0,"y":0,"w":10,"d":6}],
  "viewports":[{"sheet":"A-101","view":"Plan L1","centre":[1.2,0.9]}]}
Prints one line per kind: made/failed + first errors."""
import sys,os,json; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); fin=os.path.abspath(sys.argv[2]); fout=os.path.abspath(sys.argv[3]); F=json.load(open(sys.argv[4])); N=(json.load(open(sys.argv[5])).get('names',{}) if len(sys.argv)>5 else {})
def res(kind,v):
    if isinstance(v,int): return v
    for k in kind:
        if v in N.get(k,{}): return N[k][v]
    if isinstance(v,str) and v.lstrip('-').isdigit(): return int(v)
    raise SystemExit('cannot resolve %r (kinds %s)'%(v,kind))
def lvl(v): return res(('levels',),v)
spec=[]
def add(kind,**kw): spec.append(dict(kind=kind,**kw))
for r in F.get('rooms',[]): add('room',level=lvl(r.get('level','L1')),x=r['x'],y=r['y'],name=r.get('name',''),number=str(r.get('number','')))
for g in F.get('grids',[]): add('grid',name=g['name'],x0=g['from'][0],y0=g['from'][1],x1=g['to'][0],y1=g['to'][1])
for d in F.get('dimensions',[]):
    if 'walls' in d: add('dimwalls',view=res(('views',),d['view']),a=res(('walls',),d['walls'][0]),b=res(('walls',),d['walls'][1]),offset=d.get('offset',3.0))
    else: add('dimgrids',view=res(('views',),d['view']),a=d['grids'][0],b=d['grids'][1],offset=d.get('offset',3.0))
for t in F.get('tags',[]): add('tag',view=res(('views',),t['view']),element=res(('walls',),t['element']),x=t['at'][0],y=t['at'][1])
for t in F.get('text',[]): add('text',view=res(('views',),t['view']),x=t['x'],y=t['y'],text=t['text'])
for t in F.get('detail_lines',[]): add('dline',view=res(('views',),t['view']),x0=t['from'][0],y0=t['from'][1],x1=t['to'][0],y1=t['to'][1])
for t in F.get('filled_regions',[]): add('fregion',view=res(('views',),t['view']),x=t['x'],y=t['y'],w=t['w'],d=t['d'])
for t in F.get('viewports',[]): add('viewport',sheet=res(('sheets',),t['sheet']),view=res(('views',),t['view']),x=t['centre'][0],y=t['centre'][1])
rows=';\n'.join('  items.Add(new Dictionary<string, object> { %s })'%', '.join('{ "%s", %s }'%(k,(json.dumps(v) if not isinstance(v,str) else json.dumps(v))) for k,v in it.items()) for it in spec)
CS=r'''
using Autodesk.Revit.DB; using Autodesk.Revit.DB.Architecture; using Autodesk.Revit.DB.Structure; using System.Linq; using System.Collections.Generic; using System.Text;
Func<ElementId, long> IV = id => { var p = id.GetType().GetProperty("Value") ?? id.GetType().GetProperty("IntegerValue"); return Convert.ToInt64(p.GetValue(id, null)); };
Func<long, ElementId> EID = v => { var c = typeof(ElementId).GetConstructor(new[] { typeof(long) }); return c != null ? (ElementId)c.Invoke(new object[] { v }) : (ElementId)typeof(ElementId).GetConstructor(new[] { typeof(int) }).Invoke(new object[] { (int)v }); };
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\wl\fa_in.rte");
var items = new List<Dictionary<string, object>>();
__ROWS__;
Func<object, double> D = o => Convert.ToDouble(o); Func<object, long> L = o => Convert.ToInt64(o);
var made = new Dictionary<string, int>(); var failed = new Dictionary<string, int>(); var errs = new List<string>();
Action<string, bool, string> Rec = (k, ok, m) => { var t = ok ? made : failed; int c; t.TryGetValue(k, out c); t[k] = c + 1; if (!ok && errs.Count < 12) errs.Add(k + ":" + m); };
var gridsMade = new Dictionary<string, Grid>();
// 1. openings (first: it deletes + recreates hosted instances)
bool openings = __OPENINGS__;
if (openings) {
  var fis = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Host is Wall && f.Location is LocationPoint && f.Category != null && (IV(f.Category.Id) == (long)(int)BuiltInCategory.OST_Doors || IV(f.Category.Id) == (long)(int)BuiltInCategory.OST_Windows)).ToList();
  var info = fis.Select(f => new { sym = f.Symbol, host = (Wall)f.Host, pt = ((LocationPoint)f.Location).Point, lv = d.GetElement(f.LevelId) as Level, flip = f.FacingFlipped, hflip = f.HandFlipped, id = f.Id }).ToList();
  using (var t = new Transaction(d, "reopen")) { t.Start(); foreach (var i in info) d.Delete(i.id); d.Regenerate(); var cr = new List<FamilyInstance>();
    foreach (var i in info) { try { if (!i.sym.IsActive) i.sym.Activate(); cr.Add(d.Create.NewFamilyInstance(i.pt, i.sym, i.host, i.lv, StructuralType.NonStructural)); } catch (Exception ex) { cr.Add(null); Rec("openings", false, ex.Message); } }
    d.Regenerate(); for (int k = 0; k < info.Count; k++) { if (cr[k] == null) continue; try { if (cr[k].FacingFlipped != info[k].flip) cr[k].flipFacing(); if (cr[k].HandFlipped != info[k].hflip) cr[k].flipHand(); Rec("openings", true, ""); } catch (Exception ex) { Rec("openings", false, ex.Message); } }
    t.Commit(); }
}
if (__TOUCH__ || items.Any(x => (string)x["kind"] == "room")) {   // Revit's cached PlanTopology of a level does not know writer-made walls until they are touched
  using (var t = new Transaction(d, "nudge")) { t.Start(); var touchIds = new FilteredElementCollector(d).OfClass(typeof(Wall)).ToElementIds().ToList(); touchIds.AddRange(new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().ToElementIds()); touchIds.AddRange(new FilteredElementCollector(d).OfClass(typeof(Floor)).ToElementIds());
    foreach (var id in touchIds) { try { ElementTransformUtils.MoveElement(d, id, new XYZ(0, 0, 0.01)); ElementTransformUtils.MoveElement(d, id, new XYZ(0, 0, -0.01)); } catch (Exception ex) { errs.Add("touch " + id + ": " + ex.Message.Split((char)10)[0]); } } t.Commit(); }
  using (var t = new Transaction(d, "rg")) { t.Start(); d.Regenerate(); t.Commit(); }
}
foreach (var it in items.Where(x => (string)x["kind"] == "tag")) {      // make sure a tag family for the element's category is loaded (load from the Revit library if not)
  try { var el = d.GetElement(EID(L(it["element"]))); string cn = el.Category.Name; string stem = cn.EndsWith("s") ? cn.Substring(0, cn.Length - 1) : cn;
    var tagCat = d.Settings.Categories.Cast<Category>().FirstOrDefault(c => c.Name == stem + " Tags");
    bool have = tagCat != null && new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().Any(f => f.Category != null && IV(f.Category.Id) == IV(tagCat.Id));
    if (!have) { var root = @"C:\ProgramData\Autodesk\RVT " + d.Application.VersionNumber + @"\Libraries"; var fp = System.IO.Directory.Exists(root) ? System.IO.Directory.GetFiles(root, "*.rfa", System.IO.SearchOption.AllDirectories).FirstOrDefault(q => System.IO.Path.GetFileName(q).StartsWith(stem + " Tag")) : null;
      if (fp != null) { Family fam; bool ok = d.LoadFamily(fp, out fam); } else { // copy a tag family from the default project template (the library may not be installed)
        var tp = @"C:\\ProgramData\\Autodesk\\RVT " + d.Application.VersionNumber + @"\\Templates\\Default_M_ENU.rte"; var src = d.Application.OpenDocumentFile(tp);
        var sc = src.Settings.Categories.Cast<Category>().FirstOrDefault(c => c.Name == stem + " Tags"); var sym = sc == null ? null : new FilteredElementCollector(src).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().FirstOrDefault(f => f.Category != null && IV(f.Category.Id) == IV(sc.Id));
        if (sym != null) { using (var t = new Transaction(d, "cptag")) { t.Start(); ElementTransformUtils.CopyElements(src, new List<ElementId> { sym.Id }, d, Transform.Identity, new CopyPasteOptions()); t.Commit(); } } else errs.Add("tagfamily:none in template for " + stem);
        src.Close(false); } } } catch (Exception ex) { errs.Add("tagload:" + ex.Message); }
}
var ftype = new FilteredElementCollector(d).OfClass(typeof(FilledRegionType)).FirstElementId();
var ttype = new FilteredElementCollector(d).OfClass(typeof(TextNoteType)).FirstElementId();
foreach (var kind in new[] { "grid", "room", "dimwalls", "dimgrids", "tag", "text", "dline", "fregion", "viewport" }) {
  foreach (var it in items.Where(x => (string)x["kind"] == kind)) {
    using (var t = new Transaction(d, kind)) { t.Start();
      try {
        if (kind == "grid") { var g = Grid.Create(d, Line.CreateBound(new XYZ(D(it["x0"]), D(it["y0"]), 0), new XYZ(D(it["x1"]), D(it["y1"]), 0))); g.Name = (string)it["name"]; gridsMade[(string)it["name"]] = g; }
        else if (kind == "room") { d.Regenerate(); var lv = d.GetElement(EID(L(it["level"]))) as Level; var r = d.Create.NewRoom(lv, new UV(D(it["x"]), D(it["y"]))); r.Name = (string)it["name"]; r.Number = (string)it["number"]; if (r.Area < 1e-6) throw new Exception("room not enclosed (area 0)"); }
        else if (kind == "dimwalls") { var v = d.GetElement(EID(L(it["view"]))) as View; var wa = d.GetElement(EID(L(it["a"]))) as Wall; var wb = d.GetElement(EID(L(it["b"]))) as Wall;
          var ra = HostObjectUtils.GetSideFaces(wa, ShellLayerType.Exterior)[0]; var rb = HostObjectUtils.GetSideFaces(wb, ShellLayerType.Interior)[0];
          var la = ((LocationCurve)wa.Location).Curve; var lb = ((LocationCurve)wb.Location).Curve; var pa = la.Evaluate(0.5, true); var pb = lb.Evaluate(0.5, true); var dir = (pb - pa); var ln = Line.CreateUnbound(pa + new XYZ(0, 0, 0), new XYZ(dir.X, dir.Y, 0).Normalize());
          var arr = new ReferenceArray(); arr.Append(ra); arr.Append(rb); d.Create.NewDimension(v, ln, arr); }
        else if (kind == "dimgrids") { var v = d.GetElement(EID(L(it["view"]))) as View; var ga = gridsMade[(string)it["a"]]; var gb = gridsMade[(string)it["b"]]; var ca = (Line)ga.Curve; var cb = (Line)gb.Curve;
          var arr = new ReferenceArray(); arr.Append(new Reference(ga)); arr.Append(new Reference(gb)); var mid = (ca.GetEndPoint(0) + ca.GetEndPoint(1)) / 2; var dr = (cb.GetEndPoint(0) - ca.GetEndPoint(0)); var nrm = new XYZ(dr.X, dr.Y, 0).Normalize();
          var p0 = mid + new XYZ(0, 0, 0); d.Create.NewDimension(v, Line.CreateBound(p0, p0 + nrm * 10), arr); }
        else if (kind == "tag") { var v = d.GetElement(EID(L(it["view"]))) as View; var el = d.GetElement(EID(L(it["element"]))); IndependentTag.Create(d, v.Id, new Reference(el), false, TagMode.TM_ADDBY_CATEGORY, TagOrientation.Horizontal, new XYZ(D(it["x"]), D(it["y"]), 0)); }
        else if (kind == "text") { TextNote.Create(d, EID(L(it["view"])), new XYZ(D(it["x"]), D(it["y"]), 0), (string)it["text"], ttype); }
        else if (kind == "dline") { var v = d.GetElement(EID(L(it["view"]))) as View; d.Create.NewDetailCurve(v, Line.CreateBound(new XYZ(D(it["x0"]), D(it["y0"]), 0), new XYZ(D(it["x1"]), D(it["y1"]), 0))); }
        else if (kind == "fregion") { double x = D(it["x"]), y = D(it["y"]), w = D(it["w"]), dd = D(it["d"]); var lp = new CurveLoop(); var p = new[] { new XYZ(x, y, 0), new XYZ(x + w, y, 0), new XYZ(x + w, y + dd, 0), new XYZ(x, y + dd, 0) }; for (int i = 0; i < 4; i++) lp.Append(Line.CreateBound(p[i], p[(i + 1) % 4])); FilledRegion.Create(d, ftype, EID(L(it["view"])), new List<CurveLoop> { lp }); }
        else if (kind == "viewport") { Viewport.Create(d, EID(L(it["sheet"])), EID(L(it["view"])), new XYZ(D(it["x"]), D(it["y"]), 0)); }
        t.Commit(); Rec(kind, true, "");
      } catch (Exception ex) { t.RollBack(); Rec(kind, false, ex.Message.Replace("\n", " ")); }
    }
  }
}
int rephased = 0, rephfail = 0;
try { Phase ph1 = null; foreach (Phase pp in d.Phases) if (pp.Name == "Phase 1") ph1 = pp; if (ph1 == null) ph1 = d.Phases.get_Item(0);
  using (var tp = new Transaction(d, "phase1")) { tp.Start();
    foreach (var e in new FilteredElementCollector(d).WhereElementIsNotElementType().ToElements()) {
      if (!(e is Wall || e is FamilyInstance || e is Floor || e is Autodesk.Revit.DB.Architecture.Room)) continue;
      try { if (e.CreatedPhaseId == ph1.Id) continue; var pm = e.get_Parameter(BuiltInParameter.PHASE_CREATED); if (pm != null && !pm.IsReadOnly) { pm.Set(ph1.Id); rephased++; } else rephfail++; } catch { rephfail++; } }
    tp.Commit(); } } catch (Exception ex) { errs.Add("rephase " + ex.Message.Replace("\n", " ")); }
Console.WriteLine("REPHASED " + rephased + " failed " + rephfail);
d.SaveAs(@"C:\wl\out\fa_out.rte", new SaveAsOptions { OverwriteExistingFile = true }); d.Close(false);
Console.WriteLine("FINISHED made=" + string.Join(",", made.Select(k => k.Key + ":" + k.Value)) + " failed=" + string.Join(",", failed.Select(k => k.Key + ":" + k.Value)) + " errors=" + string.Join(" | ", errs));
'''.replace('__ROWS__',rows).replace('__OPENINGS__','true' if F.get('openings') else 'false').replace('__TOUCH__','true' if F.get('touch_walls') else 'false')
with guest.vmlock():
    guest.put(fin,'C:/wl/fa_in.rte'); p=guest.fresh(year)
    o=guest.run_job(year,p,CS,'fa',1200); print(o[-2500:])
    if 'FINISHED' in o: guest.get('C:/wl/out/fa_out.rte',fout)
    guest.down(year)
