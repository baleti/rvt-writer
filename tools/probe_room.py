import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); fin=os.path.abspath(sys.argv[2])
CS=r'''
using Autodesk.Revit.DB; using Autodesk.Revit.DB.Architecture; using System.Linq; using System.Collections.Generic;
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\wl\pr_in.rte");
var rooms = new FilteredElementCollector(d).OfClass(typeof(SpatialElement)).Cast<SpatialElement>().Where(x => x is Room).Cast<Room>().ToList();
foreach (var r in rooms) { string o = "ROOM " + r.Id + " " + r.Number; try { o += " area=" + r.Area; } catch (Exception e1) { o += " AREAERR"; } try { o += " placed=" + (r.Location != null); } catch { } try { o += " lvl=" + r.LevelId; } catch { } try { var sg = r.GetBoundarySegments(new SpatialElementBoundaryOptions()); o += " segs=" + (sg == null ? "null" : sg.Count.ToString()); } catch (Exception e2) { o += " SEGERR " + e2.Message.Split((char)10)[0]; } Console.WriteLine(o); }
var walls = new FilteredElementCollector(d).OfClass(typeof(Wall)).Cast<Wall>().ToList();
foreach (var w in walls.Where(w => w.Id.IntegerValue > 301590)) { var p = w.get_Parameter(BuiltInParameter.WALL_ATTR_ROOM_BOUNDING); Console.WriteLine("WALL " + w.Id + " roomBounding=" + (p != null ? p.AsInteger().ToString() : "null") + " lvl=" + w.LevelId); }
using (var t = new Transaction(d, "nudge")) { t.Start(); foreach (var w in walls.Where(w => w.Id.IntegerValue > 301590)) { ElementTransformUtils.MoveElement(d, w.Id, new XYZ(0, 0, 0.001)); ElementTransformUtils.MoveElement(d, w.Id, new XYZ(0, 0, -0.001)); } t.Commit(); }
foreach (var r in rooms) Console.WriteLine("AFTERNUDGE " + r.Id + " area=" + r.Area);
using (var t = new Transaction(d, "newroom")) { t.Start(); try { var lv = d.GetElement(new ElementId(301592)) as Level; var nr = d.Create.NewRoom(lv, new UV(70, 12)); Console.WriteLine("NEWROOM area=" + nr.Area + " id=" + nr.Id); } catch (Exception ex) { Console.WriteLine("NEWROOM ERR " + ex.Message.Split((char)10)[0]); } t.Commit(); }
d.Close(false);
'''
with guest.vmlock():
    guest.put(fin,'C:/wl/pr_in.rte'); p=guest.fresh(year)
    print(guest.run_job(year,p,CS,'pr',600)[-3000:]); guest.down(year)
