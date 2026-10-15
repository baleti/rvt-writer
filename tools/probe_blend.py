#!/usr/bin/env python3
import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1])
CS=r'''
using Autodesk.Revit.DB; using System.Linq; using System.Collections.Generic;
var app = UIApp.Application; var res = new List<string>();
Func<Document> nf = () => app.NewFamilyDocument(@"C:\ProgramData\Autodesk\RVT __Y__\Family Templates\English\Metric Generic Model.rft");
Func<double, double, double, CurveArray> sq = (h, z, dx) => { var ca = new CurveArray(); var p = new XYZ[] { new XYZ(-h+dx,-h,z), new XYZ(h+dx,-h,z), new XYZ(h+dx,h,z), new XYZ(-h+dx,h,z) }; for (int i = 0; i < 4; i++) ca.Append(Line.CreateBound(p[i], p[(i+1)%4])); return ca; };
// blend variants
foreach (var variant in new[] { "A top-first same plane", "B base-first same plane", "C top at z=4", "D refplane sketch" }) {
  var fd = nf();
  using (var t = new Transaction(fd, "b")) { t.Start();
    try { SketchPlane sp; if (variant.StartsWith("D")) { var rp = fd.FamilyCreate.NewReferencePlane(XYZ.Zero, XYZ.BasisY, XYZ.BasisX, fd.ActiveView ?? new FilteredElementCollector(fd).OfClass(typeof(View)).Cast<View>().First(v => !v.IsTemplate)); sp = SketchPlane.Create(fd, rp.GetPlane()); } else sp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ.Zero));
      Blend b;
      if (variant.StartsWith("B")) b = fd.FamilyCreate.NewBlend(true, sq(1, 0, 0), sq(0.5, 0, 0), sp);
      else if (variant.StartsWith("C")) b = fd.FamilyCreate.NewBlend(true, sq(0.5, 4, 0), sq(1, 0, 0), sp);
      else b = fd.FamilyCreate.NewBlend(true, sq(0.5, 0, 0), sq(1, 0, 0), sp);
      try { b.TopOffset = 4; } catch (Exception ex2) { res.Add(variant + " offset: " + ex2.Message.Split('\n')[0]); }
      res.Add(variant + " OK id=" + b.Id); } catch (Exception ex) { res.Add(variant + " FAIL " + ex.GetType().Name + ": " + ex.Message.Split('\n')[0]); }
    t.Commit(); }
  fd.Close(false);
}
// sweep variants
Func<XYZ, XYZ, XYZ, CurveArrArray> rect = (o, u, w) => { var ca = new CurveArray(); var p = new XYZ[] { o - u*0.2 - w*0.1, o + u*0.2 - w*0.1, o + u*0.2 + w*0.1, o - u*0.2 + w*0.1 }; for (int i = 0; i < 4; i++) ca.Append(Line.CreateBound(p[i], p[(i+1)%4])); var caa = new CurveArrArray(); caa.Append(ca); return caa; };
var cases = new List<Tuple<string, Func<Document, Sweep>>>();
cases.Add(Tuple.Create<string, Func<Document, Sweep>>("V1 line x, profile YZ, XY plane sketch, loc End", fd => { var sp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ.Zero)); var path = new CurveArray(); path.Append(Line.CreateBound(XYZ.Zero, new XYZ(6,0,0))); return fd.FamilyCreate.NewSweep(true, path, sp, app.Create.NewCurveLoopsProfile(rect(new XYZ(6,0,0), XYZ.BasisY, XYZ.BasisZ)), 0, ProfilePlaneLocation.End); }));
cases.Add(Tuple.Create<string, Func<Document, Sweep>>("V2 L path (2 lines), profile at start", fd => { var sp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ.Zero)); var path = new CurveArray(); path.Append(Line.CreateBound(XYZ.Zero, new XYZ(6,0,0))); path.Append(Line.CreateBound(new XYZ(6,0,0), new XYZ(6,4,0))); return fd.FamilyCreate.NewSweep(true, path, sp, app.Create.NewCurveLoopsProfile(rect(XYZ.Zero, XYZ.BasisY, XYZ.BasisZ)), 0, ProfilePlaneLocation.Start); }));
cases.Add(Tuple.Create<string, Func<Document, Sweep>>("V3 path in XZ plane (vertical), profile XY", fd => { var sp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisY, XYZ.Zero)); var path = new CurveArray(); path.Append(Line.CreateBound(XYZ.Zero, new XYZ(0,0,6))); return fd.FamilyCreate.NewSweep(true, path, sp, app.Create.NewCurveLoopsProfile(rect(XYZ.Zero, XYZ.BasisX, XYZ.BasisY)), 0, ProfilePlaneLocation.Start); }));
cases.Add(Tuple.Create<string, Func<Document, Sweep>>("V4 profile via model curves + 3D path reference", fd => { var sp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ.Zero)); var mc = fd.FamilyCreate.NewModelCurve(Line.CreateBound(XYZ.Zero, new XYZ(6,0,0)), sp); var ra = new ReferenceArray(); ra.Append(mc.GeometryCurve.Reference); return fd.FamilyCreate.NewSweep(true, ra, app.Create.NewCurveLoopsProfile(rect(XYZ.Zero, XYZ.BasisY, XYZ.BasisZ)), 0, ProfilePlaneLocation.Start); }));
cases.Add(Tuple.Create<string, Func<Document, Sweep>>("V5 path at z=1 elevated sketch plane", fd => { var sp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, new XYZ(0,0,1))); var path = new CurveArray(); path.Append(Line.CreateBound(new XYZ(0,0,1), new XYZ(6,0,1))); return fd.FamilyCreate.NewSweep(true, path, sp, app.Create.NewCurveLoopsProfile(rect(new XYZ(0,0,1), XYZ.BasisY, XYZ.BasisZ)), 0, ProfilePlaneLocation.Start); }));
foreach (var c in cases) {
  var fd = nf();
  using (var t = new Transaction(fd, "s")) { t.Start(); try { var sw = c.Item2(fd); res.Add(c.Item1 + " OK id=" + sw.Id); } catch (Exception ex) { res.Add(c.Item1 + " FAIL " + ex.GetType().Name + ": " + ex.Message.Split('\n')[0]); } t.Commit(); }
  fd.Close(false);
}
Console.WriteLine("PROBE " + string.Join(" || ", res));
'''.replace('__Y__',str(year))
with guest.vmlock():
    p=guest.fresh(year); print(guest.run_job(year,p,CS,'pb',900)[-3000:]); guest.down(year)
