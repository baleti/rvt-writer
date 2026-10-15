#!/usr/bin/env python3
"""finish_openings.py YEAR IN OUT : Revit finishing pass for hosted doors/windows of ANY geometry: every hosted FamilyInstance (door/window) of a writer-built file is re-created
by the Revit API at the same location on the same host wall (NewFamilyInstance), which makes Revit cut the openings in the walls (the writer itself cuts only the fitted case).
Output is Revit-saved (flagged). Prints wall volume before/after, instance counts and max position error."""
import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); fin=os.path.abspath(sys.argv[2]); fout=os.path.abspath(sys.argv[3])
CS=r'''
using Autodesk.Revit.DB; using Autodesk.Revit.DB.Structure; using System.Linq; using System.Collections.Generic;
Func<ElementId, long> IV = id => { var p = id.GetType().GetProperty("Value") ?? id.GetType().GetProperty("IntegerValue"); return Convert.ToInt64(p.GetValue(id, null)); };
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\wl\fo_in.rte");
Func<double> vol = () => { double s = 0; foreach (var w in new FilteredElementCollector(d).OfClass(typeof(Wall)).Cast<Wall>()) { var g = w.get_Geometry(new Options()); if (g == null) continue; foreach (var o in g) { var so = o as Solid; if (so != null) s += so.Volume; } } return s; };
double v0 = vol();
var fis = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Host is Wall && f.Location is LocationPoint && f.Category != null && (IV(f.Category.Id) == (long)(int)BuiltInCategory.OST_Doors || IV(f.Category.Id) == (long)(int)BuiltInCategory.OST_Windows)).ToList();
var info = fis.Select(f => new { sym = f.Symbol, host = (Wall)f.Host, pt = ((LocationPoint)f.Location).Point, lv = d.GetElement(f.LevelId) as Level, flip = f.FacingFlipped, hflip = f.HandFlipped, id = f.Id, mark = f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() }).ToList();
int made = 0; double maxerr = 0; var errs = new List<string>(); var created = new List<FamilyInstance>();
using (var t = new Transaction(d, "reopen")) { t.Start();
 foreach (var i in info) d.Delete(i.id);
 d.Regenerate();
 foreach (var i in info) { try { if (!i.sym.IsActive) i.sym.Activate(); var n = d.Create.NewFamilyInstance(i.pt, i.sym, i.host, i.lv, StructuralType.NonStructural); created.Add(n); made++; } catch (Exception ex) { errs.Add("create:" + ex.Message); created.Add(null); } }
 d.Regenerate();
 for (int k = 0; k < info.Count; k++) { var n = created[k]; if (n == null) continue; try { if (n.FacingFlipped != info[k].flip) n.flipFacing(); if (n.HandFlipped != info[k].hflip) n.flipHand(); } catch { }
   var q = ((LocationPoint)n.Location).Point; double e1 = q.DistanceTo(info[k].pt); maxerr = Math.Max(maxerr, e1); if (e1 > 0.01) errs.Add(info[k].sym.Name + " old=" + info[k].pt + " new=" + q); }
 t.Commit(); }
double v1 = vol();
d.SaveAs(@"C:\wl\out\fo_out.rte", new SaveAsOptions { OverwriteExistingFile = true }); d.Close(false);
Console.WriteLine("FINISHED instances=" + info.Count + " made=" + made + " maxerr=" + maxerr + " vol_before=" + v0 + " vol_after=" + v1 + " errors=" + string.Join("|", errs.Take(12)));
'''
with guest.vmlock():
    guest.put(fin,'C:/wl/fo_in.rte'); p=guest.fresh(year)
    o=guest.run_job(year,p,CS,'fo',900); print(o[-1500:])
    if 'FINISHED' in o: guest.get('C:/wl/out/fo_out.rte',fout)
    guest.down(year)
