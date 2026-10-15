#!/usr/bin/env python3
import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); fin=os.path.abspath(sys.argv[2]); x=float(sys.argv[3]); y=float(sys.argv[4])
CS=r'''
using Autodesk.Revit.DB; using Autodesk.Revit.DB.Architecture; using System.Linq; using System.Collections.Generic;
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\wl\dr_in.rte");
foreach (var w in new FilteredElementCollector(d).OfClass(typeof(Wall)).Cast<Wall>()) { var lc = w.Location as LocationCurve; var c = lc == null ? null : lc.Curve;
  Console.WriteLine("WALL " + w.Id + " " + (c == null ? "noloc" : c.GetEndPoint(0) + "->" + c.GetEndPoint(1)) + " rb=" + w.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING).AsInteger() + " lvl=" + w.LevelId + " base=" + w.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).AsDouble() + " h=" + w.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble() + " top=" + w.get_Parameter(BuiltInParameter.WALL_HEIGHT_TYPE).AsElementId() + " w=" + w.Width + " phase=" + w.CreatedPhaseId + " joinS=" + WallUtils.IsWallJoinAllowedAtEnd(w, 0) + " type=" + w.WallType.Name); }
foreach (Level l in new FilteredElementCollector(d).OfClass(typeof(Level))) Console.WriteLine("LEVEL " + l.Id + " " + l.Name + " " + l.Elevation);
var lv = new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().First(q => q.Name == "Level 1" || q.Elevation == 0);
using (var t = new Transaction(d, "r")) { t.Start(); d.Regenerate(); var r = d.Create.NewRoom(lv, new UV(__X__, __Y__)); Console.WriteLine("ROOM area=" + r.Area + " level=" + lv.Name + " loc=" + (r.Location as LocationPoint)?.Point); 
  try { var sb = new SpatialElementBoundaryOptions(); var segs = r.GetBoundarySegments(sb); Console.WriteLine("BOUNDARY loops=" + (segs == null ? -1 : segs.Count)); } catch (Exception ex) { Console.WriteLine("BNDERR " + ex.Message); }
  foreach (var ph in d.Phases.Cast<Phase>()) Console.WriteLine("PHASE " + ph.Id + " " + ph.Name); Console.WriteLine("ROOMPHASE " + r.get_Parameter(BuiltInParameter.ROOM_PHASE).AsElementId());
  var topo = d.get_PlanTopology(lv); int nc = 0; foreach (PlanCircuit c in topo.Circuits) { nc++; Console.WriteLine("CIRCUIT area=" + c.Area + " isRoomLocated=" + c.IsRoomLocated + " side=" + c.SideNum + " pt0=" + (c.GetPointInside() == null ? "none" : c.GetPointInside().ToString())); } Console.WriteLine("CIRCUITS " + nc);
  t.RollBack(); }
d.Close(false);
'''.replace('__X__',str(x)).replace('__Y__',str(y))
with guest.vmlock():
    guest.put(fin,'C:/wl/dr_in.rte'); p=guest.fresh(year)
    print(guest.run_job(year,p,CS,'dr',600)[-3000:]); guest.down(year)
