#!/usr/bin/env python3
"""regen.py YEAR IN OUT : open a (writer-built) file in Revit, nudge every wall (move +dz and back) so Revit rebuilds wall geometry incl. hosted openings, SaveAs OUT. Prints wall volumes before/after."""
import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); fin=os.path.abspath(sys.argv[2]); fout=os.path.abspath(sys.argv[3])
CS=r'''
using Autodesk.Revit.DB; using System.Linq; using System.Collections.Generic;
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\wl\regen_in.rte");
Func<double> vol = () => { double s = 0; foreach (var w in new FilteredElementCollector(d).OfClass(typeof(Wall)).Cast<Wall>()) { var g = w.get_Geometry(new Options()); if (g == null) continue; foreach (var o in g) { var so = o as Solid; if (so != null) s += so.Volume; } } return s; };
double v0 = vol(); var ids = new FilteredElementCollector(d).OfClass(typeof(Wall)).ToElementIds().ToList();
using (var t = new Transaction(d, "nudge")) { t.Start(); foreach (var id in ids) { ElementTransformUtils.MoveElement(d, id, new XYZ(0, 0, 0.01)); ElementTransformUtils.MoveElement(d, id, new XYZ(0, 0, -0.01)); }
 var fis = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Host != null).Select(f => f.Id).ToList();
 foreach (var id in fis) { ElementTransformUtils.MoveElement(d, id, new XYZ(0.01, 0, 0)); ElementTransformUtils.MoveElement(d, id, new XYZ(-0.01, 0, 0)); }
 Console.WriteLine("NUDGED instances=" + fis.Count); t.Commit(); }
double v1 = vol();
d.SaveAs(@"C:\wl\out\regen_out.rte", new SaveAsOptions { OverwriteExistingFile = true }); d.Close(false);
Console.WriteLine("REGEN walls=" + ids.Count + " vol_before=" + v0 + " vol_after=" + v1);
'''
with guest.vmlock():
    guest.put(fin,'C:/wl/regen_in.rte'); p=guest.fresh(year)
    o=guest.run_job(year,p,CS,'regen',600); print(o[-600:])
    if 'REGEN' in o: guest.get('C:/wl/out/regen_out.rte',fout)
    guest.down(year)
