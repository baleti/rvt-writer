import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
CS=r'''
using Autodesk.Revit.DB; using System.Linq;
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\ProgramData\Autodesk\RVT 2024\Templates\Default_M_ENU.rte");
Console.WriteLine("PROBE roofTypes=" + new FilteredElementCollector(d).OfClass(typeof(RoofType)).GetElementCount() + " ceilingTypes=" + new FilteredElementCollector(d).OfClass(typeof(CeilingType)).GetElementCount() + " levels=" + string.Join(",", new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().Select(l => l.Name + "@" + l.Elevation)));
foreach (var rt in new FilteredElementCollector(d).OfClass(typeof(RoofType)).Cast<RoofType>().Take(5)) Console.WriteLine("RT " + rt.Name + " " + rt.GetType().Name);
foreach (var e in new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_Roofs).WhereElementIsElementType().Take(5)) Console.WriteLine("RC " + e.Name + " " + e.GetType().Name);
d.Close(false);
'''
with guest.vmlock():
    p=guest.fresh(2024); print(guest.run_job(2024,p,CS,'proberoof',400)[-1500:]); guest.down(2024)
