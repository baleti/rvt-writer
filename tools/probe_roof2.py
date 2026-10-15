import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
CS=r'''
using Autodesk.Revit.DB; using System.Linq;
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\ProgramData\Autodesk\RVT 2024\Templates\Default_M_ENU.rte");
var l1 = new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().First(x => x.Name == "Level 1");
var rt = new FilteredElementCollector(d).OfClass(typeof(RoofType)).Cast<RoofType>().First(x => x.Name.StartsWith("Generic Roof - 300"));
Console.WriteLine("ARGS l1=" + (l1 != null) + " rt=" + (rt != null) + " family=" + rt.FamilyName);
using (var t = new Transaction(d, "roof")) { t.Start();
 var ca = new CurveArray(); var p = new XYZ[] { new XYZ(0,0,0), new XYZ(30,0,0), new XYZ(30,20,0), new XYZ(0,20,0) }; for (int i = 0; i < 4; i++) ca.Append(Line.CreateBound(p[i], p[(i+1)%4]));
 try { ModelCurveArray mca = new ModelCurveArray(); var roof = d.Create.NewFootPrintRoof(ca, l1, rt, out mca); Console.WriteLine("ROOF OK " + roof.Id + " curves=" + mca.Size); foreach (ModelCurve mc in mca) roof.set_DefinesSlope(mc, false); } catch (Exception ex) { Console.WriteLine("ROOF ERR " + ex.GetType().Name + " " + ex.Message.Split((char)10)[0] + " | " + ex.StackTrace.Split((char)10)[0]); }
 try { var ct = new FilteredElementCollector(d).OfClass(typeof(CeilingType)).Cast<CeilingType>().First(); var loop = new CurveLoop(); for (int i = 0; i < 4; i++) loop.Append(Line.CreateBound(p[i], p[(i+1)%4])); var ce = Ceiling.Create(d, new System.Collections.Generic.List<CurveLoop> { loop }, ct.Id, l1.Id); Console.WriteLine("CEILING OK " + ce.Id); } catch (Exception ex) { Console.WriteLine("CEILING ERR " + ex.Message.Split((char)10)[0]); }
 t.Commit(); }
d.Close(false);
'''
with guest.vmlock():
    p=guest.fresh(2024); print(guest.run_job(2024,p,CS,'proberoof2',400)[-1500:]); guest.down(2024)
