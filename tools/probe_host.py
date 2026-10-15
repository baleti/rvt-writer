import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); fin=os.path.abspath(sys.argv[2])
CS=r'''
using Autodesk.Revit.DB; using System.Linq; using System.Collections.Generic;
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\wl\probe_in.rte");
Func<Wall, double> wv = (w) => { double s = 0; var g = w.get_Geometry(new Options()); if (g != null) foreach (var o in g) { var so = o as Solid; if (so != null) s += so.Volume; } return s; };
var wall = d.GetElement(new ElementId(301553)) as Wall;
Console.WriteLine("PROBE wall volume " + wv(wall));
var fis = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Host != null && f.Host.Id.ToString() == "301553").ToList();
Console.WriteLine("PROBE hosted by 301553: " + fis.Count + " ids " + string.Join(",", fis.Select(f => f.Id.ToString())));
var mine = fis.Where(f => f.Id.IntegerValue > 301559 || true).Last();
using (var t = new Transaction(d, "mv")) { t.Start(); ElementTransformUtils.MoveElement(d, mine.Id, new XYZ(0.5, 0, 0)); t.Commit(); }
Console.WriteLine("PROBE after real move of " + mine.Id + ": wall volume " + wv(wall));
using (var t = new Transaction(d, "rg")) { t.Start(); var l = wall.Location as LocationCurve; ElementTransformUtils.MoveElement(d, wall.Id, new XYZ(0, 0.5, 0)); t.Commit(); }
Console.WriteLine("PROBE after moving wall: wall volume " + wv(wall));
d.Close(false);
'''
with guest.vmlock():
    guest.put(fin,'C:/wl/probe_in.rte'); p=guest.fresh(year)
    print(guest.run_job(year,p,CS,'probe',600)[-900:]); guest.down(year)
