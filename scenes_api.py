#!/usr/bin/env python3
"""scenes_api.py YEAR NAME STOREYS [SEED] : populated building built with the Revit API (Stage A: Revit-written, not writer output).
Output: C:/wl/out/scene_<NAME>.rte -> scenes/<year>_<NAME>.rte ; ground truth dump gt_geom/<year>_scene_<NAME>.tsv ; scenes/<year>_<NAME>.report.txt"""
import sys,os
WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); name=sys.argv[2]; storeys=int(sys.argv[3]); seed=int(sys.argv[4]) if len(sys.argv)>4 else 1
CS=r'''
using Autodesk.Revit.DB; using Autodesk.Revit.DB.Architecture; using Autodesk.Revit.DB.Structure; using System.Linq; using System.Collections.Generic;
var app = UIApp.Application; var rnd = new Random(__SEED__); int N = __N__; var rep = new List<string>(); var cnt = new Dictionary<string,int>();
Action<string> bump = (k) => { int c; cnt.TryGetValue(k, out c); cnt[k] = c + 1; };
var d = app.OpenDocumentFile(@"C:\wl\__SEED_FILE__");
Func<Action, string, bool> tx = (a, nm) => { using (var t = new Transaction(d, nm)) { t.Start(); try { a(); t.Commit(); return true; } catch (Exception ex) { rep.Add("FAIL " + nm + ": " + ex.Message.Split('\n')[0]); if (t.GetStatus() == TransactionStatus.Started) t.RollBack(); return false; } } };
var l1 = d.GetElement(new ElementId(355)) as Level;
var levels = new List<Level> { l1 };
double storeyH = 12;
tx(() => { l1.Name = "Level 01"; l1.Elevation = 0; for (int i = 1; i <= N; i++) { var l = Level.Create(d, storeyH * i); l.Name = (i == N ? "Roof " : "Level ") + (i + 1).ToString("00"); levels.Add(l); bump("Level"); } }, "levels");
double W = 60, D = 40;
tx(() => { for (int i = 0; i <= 6; i++) { var g = Grid.Create(d, Line.CreateBound(new XYZ(i * W / 6, -5, 0), new XYZ(i * W / 6, D + 5, 0))); g.Name = "" + (char)('A' + i); bump("Grid"); }
  for (int j = 0; j <= 4; j++) { var g = Grid.Create(d, Line.CreateBound(new XYZ(-5, j * D / 4, 0), new XYZ(W + 5, j * D / 4, 0))); g.Name = "" + (j + 1); bump("Grid"); } }, "grids");
var wts = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().Where(x => x.Kind == WallKind.Basic).ToList();
rep.Add("wallTypes: " + string.Join(" | ", wts.Select(x => x.Name)));
var extT = wts.FirstOrDefault(x => x.Name.Contains("Brick") || x.Name.Contains("Exterior")) ?? wts.First();
var intT = wts.FirstOrDefault(x => x.Name.Contains("Interior") || x.Name.Contains("Partition")) ?? wts.Last();
var doorS = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Doors).Cast<FamilySymbol>().ToList();
var winS = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().ToList();
var colS = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_StructuralColumns).Cast<FamilySymbol>().ToList();
var floorT = new FilteredElementCollector(d).OfClass(typeof(FloorType)).Cast<FloorType>().ToList();
foreach (var s in doorS.Concat(winS).Concat(colS)) if (!s.IsActive) tx(() => s.Activate(), "act");
tx(() => d.Regenerate(), "regen");
for (int i = 0; i < N; i++) {
  var lv = levels[i]; var top = levels[i + 1];
  var ext = new List<Wall>();
  tx(() => {
    var p = new XYZ[] { new XYZ(0,0,0), new XYZ(W,0,0), new XYZ(W,D,0), new XYZ(0,D,0) };
    for (int k = 0; k < 4; k++) { var w = Wall.Create(d, Line.CreateBound(p[k], p[(k + 1) % 4]), extT.Id, lv.Id, storeyH, 0, false, true); w.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).Set(top.Id); w.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("EW" + (i + 1) + "." + (k + 1)); w.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("exterior wall storey " + (i + 1)); ext.Add(w); bump("Wall"); }
    for (int j = 1; j < 3; j++) { var w = Wall.Create(d, Line.CreateBound(new XYZ(W * j / 3, 0, 0), new XYZ(W * j / 3, D, 0)), intT.Id, lv.Id, storeyH, 0, false, false); w.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("IW" + (i + 1) + "." + j); bump("Wall"); }
    var wm = Wall.Create(d, Line.CreateBound(new XYZ(0, D / 2, 0), new XYZ(W, D / 2, 0)), intT.Id, lv.Id, storeyH, 0, false, false); bump("Wall");
  }, "walls" + i);
  tx(() => d.Regenerate(), "regen");
  tx(() => {
    for (int k = 0; k < ext.Count; k++) {
      var w = ext[k]; var lc = (w.Location as LocationCurve).Curve; double L = lc.Length;
      if (doorS.Count > 0 && k == 0 && i == 0) { var fi = d.Create.NewFamilyInstance(lc.Evaluate(0.3, true), doorS[rnd.Next(doorS.Count)], w, lv, StructuralType.NonStructural); fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("D" + (i + 1) + ".1"); bump("Door"); }
      if (winS.Count > 0) for (int m = 1; m <= 4; m++) { var ws = winS[rnd.Next(winS.Count)]; var fi = d.Create.NewFamilyInstance(lc.Evaluate(m / 5.0, true) + new XYZ(0, 0, 3), ws, w, lv, StructuralType.NonStructural); fi.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("W" + (i + 1) + "." + k + "." + m); bump("Window"); }
    } }, "hosted" + i);
  tx(() => { if (colS.Count > 0) for (int gx = 0; gx <= 6; gx += 2) for (int gy = 0; gy <= 4; gy += 2) { var c = d.Create.NewFamilyInstance(new XYZ(gx * W / 6, gy * D / 4, 0), colS[0], lv, StructuralType.Column); try { c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(top.Id); } catch { } bump("Column"); } }, "cols" + i);
  tx(() => { var loop = new CurveLoop(); var p = new XYZ[] { new XYZ(0,0,0), new XYZ(W,0,0), new XYZ(W,D,0), new XYZ(0,D,0) }; for (int k = 0; k < 4; k++) loop.Append(Line.CreateBound(p[k], p[(k + 1) % 4])); var f = Floor.Create(d, new List<CurveLoop> { loop }, floorT[i % floorT.Count].Id, lv.Id); f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("F" + (i + 1)); bump("Floor"); }, "floor" + i);
  tx(() => d.Regenerate(), "regen");
  tx(() => {
    string[] names = { "Lobby", "Office", "Meeting", "Storage", "Kitchen", "WC" }; int rn = 0;
    for (int a = 0; a < 3; a++) for (int b = 0; b < 2; b++) { var r = d.Create.NewRoom(lv, new UV(W * (a + 0.5) / 3, D * (b + 0.25 + 0.5 * b) / 2 * (b == 0 ? 1 : 1))); if (r != null) { r.Name = names[rn % names.Length] + " " + (i + 1) + (char)('a' + rn); r.Number = ((i + 1) * 100 + rn + 1).ToString(); try { r.get_Parameter(BuiltInParameter.ROOM_DEPARTMENT).Set(rn % 2 == 0 ? "Operations" : "Admin"); } catch { } bump("Room"); rn++; } }
  }, "rooms" + i);
  if (i == 0) tx(() => { var sid = ElementId.InvalidElementId; }, "noop");
}
// stairs between level 1 and 2 (run) and a railing
if (N >= 1) {
  try { var scope = new StairsEditScope(d, "stairs"); var sid = scope.Start(levels[0].Id, levels[1].Id); using (var t = new Transaction(d, "run")) { t.Start(); StairsRun.CreateStraightRun(d, sid, Line.CreateBound(new XYZ(W + 3, 2, 0), new XYZ(W + 3 + 20, 2, 0)), StairsRunJustification.Center); t.Commit(); } scope.Commit(new StairFail()); bump("Stairs"); } catch (Exception ex) { rep.Add("FAIL stairs: " + ex.Message.Split('\n')[0]); }
  tx(() => { var rt = new FilteredElementCollector(d).OfClass(typeof(RailingType)).FirstElement().Id; var loop = new CurveLoop(); loop.Append(Line.CreateBound(new XYZ(0, -3, 0), new XYZ(W, -3, 0))); Railing.Create(d, loop, rt, levels[0].Id); bump("Railing"); }, "railing");
}
tx(() => { var pts = new List<XYZ>(); for (int a = -2; a <= 3; a++) for (int b = -2; b <= 3; b++) pts.Add(new XYZ(-20 + a * 30, -20 + b * 25, -3 + 0.8 * Math.Sin(a + b) + rnd.NextDouble())); TopographySurface.Create(d, pts); bump("Topography"); }, "topo");
tx(() => { var plan = new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().First(x => !x.IsTemplate && x.ViewType == ViewType.FloorPlan); var tnt = new FilteredElementCollector(d).OfClass(typeof(TextNoteType)).FirstElement().Id; TextNote.Create(d, plan.Id, new XYZ(0, -10, 0), "Scene " + "__NAME__" + " seed " + __SEED__, tnt); bump("TextNote"); }, "text");
// plans per level + sheets
tx(() => {
  var vft = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.FloorPlan);
  var tb = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<FamilySymbol>().FirstOrDefault();
  for (int i = 1; i <= N; i++) { try { var vp = ViewPlan.Create(d, vft.Id, levels[i].Id); vp.Name = "Plan " + levels[i].Name; bump("ViewPlan"); if (tb != null) { var sh = ViewSheet.Create(d, tb.Id); sh.SheetNumber = "A" + (100 + i); sh.Name = "Floor plan " + levels[i].Name; Viewport.Create(d, sh.Id, vp.Id, new XYZ(1, 0.7, 0)); bump("Sheet"); bump("Viewport"); } } catch (Exception ex) { rep.Add("FAIL view " + i + ": " + ex.Message.Split('\n')[0]); } }
  var v3 = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.ThreeDimensional); var v3d = View3D.CreateIsometric(d, v3.Id); v3d.Name = "Scene 3D"; bump("View3D");
}, "views");
d.SaveAs(@"C:\wl\out\scene___NAME__.rte", new SaveAsOptions { OverwriteExistingFile = true });
int total = new FilteredElementCollector(d).WhereElementIsNotElementType().GetElementCount();
d.Close(false);
Console.WriteLine("SCENE total=" + total + " " + string.Join(",", cnt.Select(kv => kv.Key + "=" + kv.Value)));
foreach (var r in rep) Console.WriteLine("REPORT " + r);
public class StairFail : IFailuresPreprocessor { public FailureProcessingResult PreprocessFailures(FailuresAccessor a) { return FailureProcessingResult.Continue; } }
'''
seedf={2024:'ds0.rte',2026:'o26_line.rte'}[year]
guest.put(WL+'/files/'+seedf,'C:/wl/'+seedf)
tag='scene_'+name
with guest.vmlock():
    port=guest.fresh(year)
    o=guest.run_job(year,port,CS.replace('__SEED__',str(seed)).replace('__N__',str(storeys)).replace('__NAME__',name).replace('__SEED_FILE__',seedf),tag,1500)
    print(o[-3000:])
    if 'SCENE' in o:
        guest.get('C:/wl/out/%s.rte'%tag,'%s/scenes/%d_%s.rte'%(WL,year,name))
        open('%s/scenes/%d_%s.report.txt'%(WL,year,name),'w').write(o[-6000:])
    guest.down(year)
