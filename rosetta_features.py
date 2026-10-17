# feature name -> (description, parameters base/variant, C# body). Variables available: d (Document), v (int 0=base,1=variant), l1, l2 (Levels 355/2607), out (string log)
F={}
F['stair_run']=("straight stair run Level 1 -> Level 2, justification Center; base: line (0,0)-(15,0); variant: (0,0)-(17,0)",r'''
var scope = new StairsEditScope(d, "stairs"); ElementId sid = scope.Start(l1.Id, l2.Id);
using (var t = new Transaction(d, "run")) { t.Start(); StairsRun.CreateStraightRun(d, sid, Line.CreateBound(new XYZ(0,0,0), new XYZ(v==0?15:17,0,0)), StairsRunJustification.Center); t.Commit(); }
scope.Commit(new StairsFailurePreprocessor());
''')
F['railing']=("railing on level 1 along (0,0)-(20,0) (variant (0,0)-(24,0)), first RailingType in the project",r'''
using (var t = new Transaction(d, "r")) { t.Start(); var rt = new FilteredElementCollector(d).OfClass(typeof(RailingType)).FirstElement().Id;
 var loop = new CurveLoop(); loop.Append(Line.CreateBound(new XYZ(0,0,0), new XYZ(v==0?20:24,0,0))); Railing.Create(d, loop, rt, l1.Id); t.Commit(); }
''')
F['topography']=("topography surface from 5 points (0,0,0),(40,0,2),(40,40,4),(0,40,2),(20,20,5); variant: centre point z=9",r'''
using (var t = new Transaction(d, "t")) { t.Start(); var pts = new List<XYZ> { new XYZ(0,0,0), new XYZ(40,0,2), new XYZ(40,40,4), new XYZ(0,40,2), new XYZ(20,20,v==0?5:9) }; TopographySurface.Create(d, pts); t.Commit(); }
''')
F['wall_curved']=("curved wall: arc centre (0,0) radius 20 from angle 0 to 90deg on Level 1 height 10 ft; variant radius 26",r'''
using (var t = new Transaction(d, "w")) { t.Start(); double R = v==0?20:26; var arc = Arc.Create(new XYZ(R,0,0), new XYZ(0,R,0), new XYZ(R*Math.Cos(Math.PI/4), R*Math.Sin(Math.PI/4), 0));
 var w = Wall.Create(d, arc, l1.Id, false); w.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).Set(10); t.Commit(); }
''')
F['wall_profile']=("profile-edited wall: polygon (0,0),(12,0),(12,8),(6,12),(0,8) on Level 1; variant: apex (6,15)",r'''
using (var t = new Transaction(d, "w")) { t.Start(); var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic).Id;
 var pts = new XYZ[] { new XYZ(0,0,0), new XYZ(12,0,0), new XYZ(12,0,8), new XYZ(6,0,v==0?12:15), new XYZ(0,0,8) }; var prof = new List<Curve>(); for (int i = 0; i < pts.Length; i++) prof.Add(Line.CreateBound(pts[i], pts[(i+1)%pts.Length]));
 Wall.Create(d, prof, wt, l1.Id, false); t.Commit(); }
''')
F['room']=("four walls 10x8 ft on Level 1 + room at (5,4); variant 12x8",r'''
using (var t = new Transaction(d, "room")) { t.Start(); double W = v==0?10:12, H = 8; var p = new XYZ[] { new XYZ(0,0,0), new XYZ(W,0,0), new XYZ(W,H,0), new XYZ(0,H,0) };
 for (int i = 0; i < 4; i++) Wall.Create(d, Line.CreateBound(p[i], p[(i+1)%4]), l1.Id, false);
 d.Regenerate(); var r = d.Create.NewRoom(l1, new UV(W/2, H/2)); r.Name = "Rosetta room"; r.Number = "R1"; t.Commit(); }
''')
F['wall_types']=("one wall for each of the first 6 wall types of the template (basic, compound, curtain, stacked), length 10 ft along x spaced 20 ft; variant: height 15",r'''
using (var t = new Transaction(d, "w")) { t.Start(); int k = 0; foreach (var wt in new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().Take(8)) { var w = Wall.Create(d, Line.CreateBound(new XYZ(20*k,0,0), new XYZ(20*k+10,0,0)), wt.Id, l1.Id, v==0?10:15, 0, false, false); out_ += wt.Name + ";"; k++; } t.Commit(); }
''')
F['grid_level']=("grids (3 straight, 1 arc) and 2 extra levels; variant: levels at +1 ft",r'''
using (var t = new Transaction(d, "g")) { t.Start(); for (int i = 0; i < 3; i++) { var g = Grid.Create(d, Line.CreateBound(new XYZ(10*i,-5,0), new XYZ(10*i,25,0))); g.Name = "G" + (i+1); }
 var ga = Grid.Create(d, Arc.Create(new XYZ(30,0,0), new XYZ(30,20,0), new XYZ(40,10,0))); ga.Name = "GA";
 var a = Level.Create(d, 30 + (v==0?0:1)); a.Name = "Rosetta L3"; var b = Level.Create(d, 45 + (v==0?0:1)); b.Name = "Rosetta L4"; t.Commit(); }
''')
F['house']=("small house on Level 1: 4 exterior walls 40x26 ft (type with 'Brick' if any), 1 interior wall, 2 doors, 3 windows, 2 structural columns, floor, room 'Living' + tag, text note; variant = same plus an exact copy of everything translated by (100,0,0) via ElementTransformUtils.CopyElements",r'''
var made = new List<ElementId>();
using (var t = new Transaction(d, "house")) { t.Start();
 var wts = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().Where(x => x.Kind == WallKind.Basic).ToList();
 var wt = wts.FirstOrDefault(x => x.Name.Contains("Brick")) ?? wts.First(); out_ += "walltype=" + wt.Name + ";";
 var p = new XYZ[] { new XYZ(0,0,0), new XYZ(40,0,0), new XYZ(40,26,0), new XYZ(0,26,0) };
 var walls = new List<Wall>();
 for (int i = 0; i < 4; i++) { var w = Wall.Create(d, Line.CreateBound(p[i], p[(i+1)%4]), wt.Id, l1.Id, 10, 0, false, false); walls.Add(w); made.Add(w.Id); }
 var iw = Wall.Create(d, Line.CreateBound(new XYZ(20,0,0), new XYZ(20,26,0)), wts.First(x => x.Name.Contains("Interior") || x.Name.Contains("Generic")).Id, l1.Id, 10, 0, false, false); made.Add(iw.Id);
 d.Regenerate();
 var doors = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Doors).Cast<FamilySymbol>().ToList();
 var wins = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().ToList();
 var cols = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_StructuralColumns).Cast<FamilySymbol>().ToList();
 try { var ds = doors.First(); if (!ds.IsActive) ds.Activate(); made.Add(d.Create.NewFamilyInstance(new XYZ(10,0,0), ds, walls[0], l1, StructuralType.NonStructural).Id); made.Add(d.Create.NewFamilyInstance(new XYZ(20,13,0), ds, iw, l1, StructuralType.NonStructural).Id); } catch (Exception ex) { out_ += "doorERR " + ex.Message + ";"; }
 try { var cs = cols.First(); if (!cs.IsActive) cs.Activate(); made.Add(d.Create.NewFamilyInstance(new XYZ(2,2,0), cs, l1, StructuralType.Column).Id); made.Add(d.Create.NewFamilyInstance(new XYZ(38,24,0), cs, l1, StructuralType.Column).Id); } catch (Exception ex) { out_ += "colERR " + ex.Message + ";"; }
 try { var ft = new FilteredElementCollector(d).OfClass(typeof(FloorType)).Cast<FloorType>().First(); var loop = new CurveLoop(); for (int i = 0; i < 4; i++) loop.Append(Line.CreateBound(p[i], p[(i+1)%4])); made.Add(Floor.Create(d, new List<CurveLoop> { loop }, ft.Id, l1.Id).Id); } catch (Exception ex) { out_ += "floorERR " + ex.Message + ";"; }
 d.Regenerate();
 try { var room = d.Create.NewRoom(l1, new UV(10, 13)); room.Name = "Living"; room.Number = "101"; made.Add(room.Id);
   var plan = new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().First(x => !x.IsTemplate && x.GenLevel != null && x.GenLevel.Id == l1.Id && x.ViewType == ViewType.FloorPlan);
   try { made.Add(d.Create.NewRoomTag(new LinkElementId(room.Id), new UV(10, 13), plan.Id).Id); } catch (Exception ex) { out_ += "tagERR " + ex.Message + ";"; }
   try { var tnt = new FilteredElementCollector(d).OfClass(typeof(TextNoteType)).FirstElement().Id; made.Add(TextNote.Create(d, plan.Id, new XYZ(5, 30, 0), "Rosetta house note", tnt).Id); } catch (Exception ex) { out_ += "textERR " + ex.Message + ";"; } } catch (Exception ex) { out_ += "roomERR " + ex.Message + ";"; }
 t.Commit(); }
out_ += "made=" + made.Count + ";";
if (v == 1) { using (var t = new Transaction(d, "copy")) { t.Start(); var cp = ElementTransformUtils.CopyElements(d, made.Where(x => d.GetElement(x) != null && !(d.GetElement(x) is RoomTag) && !(d.GetElement(x) is TextNote)).ToList(), new XYZ(100, 0, 0)); out_ += "copied=" + cp.Count + ";"; t.Commit(); } }
''')

# ---- family form features: build a Generic Model family with ONE form, load it, place one instance
FAMPRE=r'''
public class FamLoadOpts : IFamilyLoadOptions { public bool OnFamilyFound(bool inUse, out bool overwriteParameterValues) { overwriteParameterValues = true; return true; } public bool OnSharedFamilyFound(Family sharedFamily, bool inUse, out FamilySource source, out bool overwriteParameterValues) { source = FamilySource.Family; overwriteParameterValues = true; return true; } }
Func<string, Document> newfam = (tpl) => app.NewFamilyDocument(@"C:\ProgramData\Autodesk\RVT __Y__\Family Templates\English\" + tpl);
Family loadedFam = null;
Action<Document, string> loadfam = (fd, nm) => { string pdir = @"C:\wl\out\fam" + app.VersionNumber; System.IO.Directory.CreateDirectory(pdir); string pth = pdir + @"\" + nm + ".rfa"; fd.SaveAs(pth, new SaveAsOptions { OverwriteExistingFile = true }); try { var fam0 = fd.LoadFamily(d, new FamLoadOpts()); out_ += "fdload=" + (fam0 != null) + ";"; loadedFam = fam0; } catch (Exception ex) { out_ += "fdloadERR " + ex.Message.Split('\n')[0] + ";"; } fd.Close(false); if (loadedFam == null) { Family f; bool okl = d.LoadFamily(pth, new FamLoadOpts(), out f); out_ += "load=" + okl + ";"; loadedFam = f; } };
Func<Document, SketchPlane> fplane = (fd) => { var pl = new FilteredElementCollector(fd).OfClass(typeof(SketchPlane)).Cast<SketchPlane>().FirstOrDefault(); return pl; };
'''
def famfeat(desc, build):
    body = FAMPRE + r'''
var fd = newfam("Metric Generic Model.rft"); string famname = "Rosetta_" + (v==0?"base":"var");
using (var t = new Transaction(fd, "form")) { t.Start();
 var sp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisZ, XYZ.Zero));
 var spx = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(XYZ.BasisY, XYZ.Zero));
 Func<IList<XYZ>, CurveArrArray> poly = (pts) => { var ca = new CurveArray(); for (int i = 0; i < pts.Count; i++) ca.Append(Line.CreateBound(pts[i], pts[(i+1)%pts.Count])); var caa = new CurveArrArray(); caa.Append(ca); return caa; };
''' + build + r'''
 t.Commit(); }
loadfam(fd, famname);
using (var t = new Transaction(d, "inst")) { t.Start(); var fam = loadedFam ?? new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().FirstOrDefault(x => x.Name == famname); if (fam == null) throw new Exception("family not loaded; out=" + out_ + " names: " + string.Join(",", new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().Where(x => x.Name.Contains("Rosetta")).Select(x => x.Name))); var sym = d.GetElement(fam.GetFamilySymbolIds().First()) as FamilySymbol; sym.Activate(); d.Create.NewFamilyInstance(new XYZ(5, 5, 0), sym, l1, StructuralType.NonStructural); t.Commit(); }
'''
    return (desc, body)
F['fam_extrusion_arc']=famfeat("extrusion of profile: rectangle 2x1 plus arc cap, depth 3 ft; variant depth 5",r'''
 var prof = new CurveArray(); prof.Append(Line.CreateBound(new XYZ(-1,-0.5,0), new XYZ(1,-0.5,0))); prof.Append(Line.CreateBound(new XYZ(1,-0.5,0), new XYZ(1,0.5,0))); prof.Append(Arc.Create(new XYZ(1,0.5,0), new XYZ(-1,0.5,0), new XYZ(0,1.0,0))); prof.Append(Line.CreateBound(new XYZ(-1,0.5,0), new XYZ(-1,-0.5,0)));
 var caa = new CurveArrArray(); caa.Append(prof); fd.FamilyCreate.NewExtrusion(true, caa, sp, v==0?3:5);''')
F['fam_revolution_cone']=famfeat("revolve of right triangle (r=2,h=3) around Z axis, 360 deg: a cone; variant r=3",r'''
 double R = v==0?2:3; var prof = new CurveArray(); prof.Append(Line.CreateBound(new XYZ(0,0,0), new XYZ(R,0,0))); prof.Append(Line.CreateBound(new XYZ(R,0,0), new XYZ(0,0,3))); prof.Append(Line.CreateBound(new XYZ(0,0,3), new XYZ(0,0,0)));
 var caa = new CurveArrArray(); caa.Append(prof); var axis = Line.CreateBound(new XYZ(0,0,0), new XYZ(0,0,1)); fd.FamilyCreate.NewRevolution(true, caa, spx, axis, 0, 2*Math.PI);''')
F['fam_revolution_sphere']=famfeat("revolve of half circle r=2 around Z axis: sphere; variant r=3",r'''
 double R = v==0?2:3; var prof = new CurveArray(); prof.Append(Arc.Create(new XYZ(0,0,-R), new XYZ(0,0,R), new XYZ(R,0,0))); prof.Append(Line.CreateBound(new XYZ(0,0,R), new XYZ(0,0,-R)));
 var caa = new CurveArrArray(); caa.Append(prof); fd.FamilyCreate.NewRevolution(true, caa, spx, Line.CreateBound(new XYZ(0,0,-1), new XYZ(0,0,1)), 0, 2*Math.PI);''')
F['fam_revolution_torus']=famfeat("revolve of circle r=0.5 centred x=2 around Z axis: torus; variant tube r=0.8",r'''
 double r = v==0?0.5:0.8; var prof = new CurveArray(); prof.Append(Arc.Create(new XYZ(2,0,0), r, 0, Math.PI, XYZ.BasisX, XYZ.BasisZ)); prof.Append(Arc.Create(new XYZ(2,0,0), r, Math.PI, 2*Math.PI, XYZ.BasisX, XYZ.BasisZ));
 var caa = new CurveArrArray(); caa.Append(prof); fd.FamilyCreate.NewRevolution(true, caa, spx, Line.CreateBound(new XYZ(0,0,-1), new XYZ(0,0,1)), 0, 2*Math.PI);''')
F['fam_blend']=famfeat("blend: bottom square 2x2 at z=0, top square 1x1 at z=4 (variant 6): top profile drawn AT its z (profiles on the same z make Revit throw InternalException code 1)",r'''
 double H = v==0?4:6;
 var bot = new CurveArray(); var pb = new XYZ[] { new XYZ(-1,-1,0), new XYZ(1,-1,0), new XYZ(1,1,0), new XYZ(-1,1,0) }; for (int i = 0; i < 4; i++) bot.Append(Line.CreateBound(pb[i], pb[(i+1)%4]));
 var top = new CurveArray(); var pt = new XYZ[] { new XYZ(-0.5,-0.5,H), new XYZ(0.5,-0.5,H), new XYZ(0.5,0.5,H), new XYZ(-0.5,0.5,H) }; for (int i = 0; i < 4; i++) top.Append(Line.CreateBound(pt[i], pt[(i+1)%4]));
 fd.FamilyCreate.NewBlend(true, top, bot, sp);''')
F['fam_sweep_arc_path']=famfeat("sweep of rectangle 0.4x0.2 along a quarter-circle path r=3 in the XZ plane (variant r=4): the sketch plane must be vertical (a path in the horizontal plane raised ArgumentException)",r'''
 double R = v==0?3:4; var path = new CurveArray(); path.Append(Arc.Create(new XYZ(R,0,0), new XYZ(0,0,R), new XYZ(R*Math.Cos(Math.PI/4), 0, R*Math.Sin(Math.PI/4))));
 var pr = new CurveArray(); var pts = new XYZ[] { new XYZ(R-0.2,-0.1,0), new XYZ(R+0.2,-0.1,0), new XYZ(R+0.2,0.1,0), new XYZ(R-0.2,0.1,0) }; for (int i = 0; i < 4; i++) pr.Append(Line.CreateBound(pts[i], pts[(i+1)%4]));
 var caa = new CurveArrArray(); caa.Append(pr); var sprof = app.Create.NewCurveLoopsProfile(caa); fd.FamilyCreate.NewSweep(true, path, spx, sprof, 0, ProfilePlaneLocation.Start);''')
F['fam_voidcut']=famfeat("solid box 4x4x4 minus void cylinder r=1 through; variant r=1.5",r'''
 var box = new CurveArray(); var pb = new XYZ[] { new XYZ(-2,-2,0), new XYZ(2,-2,0), new XYZ(2,2,0), new XYZ(-2,2,0) }; for (int i = 0; i < 4; i++) box.Append(Line.CreateBound(pb[i], pb[(i+1)%4]));
 var caa = new CurveArrArray(); caa.Append(box); fd.FamilyCreate.NewExtrusion(true, caa, sp, 4);
 double r = v==0?1:1.5; var c = new CurveArray(); c.Append(Arc.Create(XYZ.Zero, r, 0, Math.PI, XYZ.BasisX, XYZ.BasisY)); c.Append(Arc.Create(XYZ.Zero, r, Math.PI, 2*Math.PI, XYZ.BasisX, XYZ.BasisY));
 var caa2 = new CurveArrArray(); caa2.Append(c); fd.FamilyCreate.NewExtrusion(false, caa2, sp, 4);''')

# ---- profile features
F['prof_structural_framing']=("one structural framing beam per available framing symbol of the seed (profile families like M_W Shapes etc.), length 6 ft along x; variant: same beams, plus every symbol's instance 'Cut Length' unchanged but type parameter Height/Width of first symbol DUPLICATED to a new type 'Rosetta_Var' with dimensions +20%",r'''
using (var t = new Transaction(d, "fr")) { t.Start(); int k = 0;
 var syms = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_StructuralFraming).Cast<FamilySymbol>().ToList();
 foreach (var s in syms) { if (!s.IsActive) s.Activate(); try { var b = d.Create.NewFamilyInstance(Line.CreateBound(new XYZ(0, 3 * k, 10), new XYZ(6, 3 * k, 10)), s, l1, StructuralType.Beam); out_ += s.FamilyName + ":" + s.Name + ";"; } catch (Exception ex) { out_ += "ERR " + s.Name + ex.Message.Split('\n')[0] + ";"; } k++; }
 if (v == 1 && syms.Count > 0) { var nt = syms[0].Duplicate("Rosetta_Var") as FamilySymbol; foreach (Parameter p in nt.Parameters) { if (!p.IsReadOnly && p.StorageType == StorageType.Double && p.Definition.GetDataType() == SpecTypeId.Length) { p.Set(p.AsDouble() * 1.2); out_ += "scaled " + p.Definition.Name + ";"; } } nt.Activate(); d.Create.NewFamilyInstance(Line.CreateBound(new XYZ(0, 3 * k, 10), new XYZ(6, 3 * k, 10)), nt, l1, StructuralType.Beam); }
 t.Commit(); }
''')
F['prof_wall_sweep_reveal']=("basic wall 10 ft with a wall sweep (profile = first Profiles-category symbol 'Gutter'/'Fascia') and reveal (first 'Reveal' profile); variant: sweep distance from base 1 -> 2 ft",r'''
using (var t = new Transaction(d, "sw")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var w = Wall.Create(d, Line.CreateBound(XYZ.Zero, new XYZ(10, 0, 0)), wt.Id, l1.Id, 10, 0, false, false); d.Regenerate();
 var profs = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_ProfileFamilies).Cast<FamilySymbol>().ToList();
 var sweepP = profs.First(x => x.FamilyName.Contains("Fascia") || x.FamilyName.Contains("Gutter")); var revP = profs.First(x => x.FamilyName.Contains("Reveal"));
 var si = new WallSweepInfo(WallSweepType.Sweep, false); si.Distance = v == 0 ? 1 : 2; si.WallSide = WallSide.Exterior; var sw = WallSweep.Create(w, new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_Cornices).WhereElementIsElementType().First().Id, si);
 out_ += "sweepprofile=" + sweepP.FamilyName + ":" + sweepP.Name + ";revealprofile=" + revP.FamilyName + ":" + revP.Name + ";";
 try { var rv = new WallSweepInfo(WallSweepType.Reveal, false); rv.Distance = 5; WallSweep.Create(w, new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_Reveals).WhereElementIsElementType().First().Id, rv); } catch (Exception ex) { out_ += "revealERR " + ex.Message.Split('\n')[0] + ";"; }
 t.Commit(); }
''')
F['prof_curtain_mullion']=("curtain wall 12 ft x 10 ft with 3x2 grid and rectangular mullions on all grid lines; variant: 4x2 grid",r'''
using (var t = new Transaction(d, "cw")) { t.Start();
 var cwt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Curtain);
 var w = Wall.Create(d, Line.CreateBound(XYZ.Zero, new XYZ(12, 0, 0)), cwt.Id, l1.Id, 10, 0, false, false);
 var mt = new FilteredElementCollector(d).OfClass(typeof(MullionType)).Cast<MullionType>().First(); 
 cwt.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_HORIZ).Set(mt.Id); cwt.get_Parameter(BuiltInParameter.AUTO_MULLION_INTERIOR_VERT).Set(mt.Id); cwt.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_HORIZ).Set(mt.Id); cwt.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_HORIZ).Set(mt.Id); cwt.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER1_VERT).Set(mt.Id); cwt.get_Parameter(BuiltInParameter.AUTO_MULLION_BORDER2_VERT).Set(mt.Id);
 d.Regenerate(); var cg = w.CurtainGrid; cg.AddGridLine(true, new XYZ(0, 0, 5), false); cg.AddGridLine(false, new XYZ(4, 0, 0), false); cg.AddGridLine(false, new XYZ(8, 0, 0), false); if (v == 1) cg.AddGridLine(false, new XYZ(6, 0, 0), false);
 out_ += "mullion=" + mt.Name + ";"; t.Commit(); }
''')
F['prof_railing_handrail']=("railing along (0,0)-(10,0) with first handrail/top rail type; variant: railing type duplicated with handrail profile = a different Profiles symbol",r'''
using (var t = new Transaction(d, "rh")) { t.Start(); var rts = new FilteredElementCollector(d).OfClass(typeof(RailingType)).Cast<RailingType>().ToList(); var rt = rts.First();
 var loop = new CurveLoop(); loop.Append(Line.CreateBound(XYZ.Zero, new XYZ(10, 0, 0))); var r = Railing.Create(d, loop, rt.Id, l1.Id); out_ += "railtype=" + rt.Name + ";";
 if (v == 1) { var hrt = new FilteredElementCollector(d).OfClass(typeof(HandRailType)).Cast<HandRailType>().ToList(); var nh = hrt.First().Duplicate("Rosetta_Handrail") as HandRailType; var profs = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_ProfileFamilies).Cast<FamilySymbol>().Where(x => x.FamilyName.Contains("Handrail")).ToList(); if (profs.Count > 1) { out_ += "handrailprofile=" + profs.Last().Name + ";"; try { nh.LookupParameter("Profile").Set(profs.Last().Id); } catch (Exception ex2) { out_ += "profparamERR " + ex2.Message.Split('\n')[0] + ";"; } } }
 t.Commit(); }
''')
F['fam_sketch_profile_spline']=("Generic Model family: extrusion of a closed sketch profile = arc + hermite spline + two lines, with an inner circular hole, depth 2; variant depth 3",r'''
 var outer = new CurveArray(); outer.Append(Line.CreateBound(new XYZ(0,0,0), new XYZ(4,0,0))); outer.Append(Line.CreateBound(new XYZ(4,0,0), new XYZ(4,2,0))); 
 outer.Append(Arc.Create(new XYZ(4,2,0), new XYZ(2,3,0), new XYZ(3.3,2.8,0)));
 outer.Append(HermiteSpline.Create(new List<XYZ> { new XYZ(2,3,0), new XYZ(1,2.5,0), new XYZ(0,2,0) }, false)); outer.Append(Line.CreateBound(new XYZ(0,2,0), new XYZ(0,0,0)));
 var hole = new CurveArray(); hole.Append(Arc.Create(new XYZ(2,1,0), 0.4, 0, Math.PI, XYZ.BasisX, XYZ.BasisY)); hole.Append(Arc.Create(new XYZ(2,1,0), 0.4, Math.PI, 2*Math.PI, XYZ.BasisX, XYZ.BasisY));
 var caa = new CurveArrArray(); caa.Append(outer); caa.Append(hole); fd.FamilyCreate.NewExtrusion(true, caa, sp, v==0?2:3);''')
F['fam_sketch_profile_spline']=famfeat(*F['fam_sketch_profile_spline'])

# ---- hosted-opening differentials: what changes in the HOST WALL record when a window/door is added
_HW = r'''
using (var t = new Transaction(d, "hw")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Name.Contains("Generic - 200mm") || x.Kind == WallKind.Basic);
 var w = Wall.Create(d, Line.CreateBound(XYZ.Zero, new XYZ(20, 0, 0)), wt.Id, l1.Id, 10, 0, false, false); d.Regenerate();
 var ws = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().First(); ws.Activate();
 var ds = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Doors).Cast<FamilySymbol>().First(); ds.Activate(); d.Regenerate();
 __BODY__
 t.Commit(); }
'''
F['wall_win1']=("20 ft wall at origin; base: no opening; variant: one window (first Windows symbol) at x=8, sill 3",_HW.replace('__BODY__','if (v == 1) d.Create.NewFamilyInstance(new XYZ(8, 0, 3), ws, w, l1, StructuralType.NonStructural);'))
F['wall_win2']=("20 ft wall; base: one window at x=6; variant: second window of the same type at x=14",_HW.replace('__BODY__','d.Create.NewFamilyInstance(new XYZ(6, 0, 3), ws, w, l1, StructuralType.NonStructural); if (v == 1) d.Create.NewFamilyInstance(new XYZ(14, 0, 3), ws, w, l1, StructuralType.NonStructural);'))
F['wall_door1']=("20 ft wall; base: no opening; variant: one door (first Doors symbol) at x=10",_HW.replace('__BODY__','if (v == 1) d.Create.NewFamilyInstance(new XYZ(10, 0, 0), ds, w, l1, StructuralType.NonStructural);'))

F['floors12']=("12 rectangular floors on Level 1 (variant: Level 2), generic floor type (first FloorType), rectangle (x0,y0,W,D) = (0,0,40,26) (50,0,30,20) (100,5,12,12) (0,50,25,8) (40,50,10,30) (70,50,33,17) (110,50,20,40) (0,100,15,15) (30,100,60,10) (100,100,8,22) (120,100,45,45) (0,130,18,9); curve loop counter-clockwise from (x0,y0)",r'''
using (var t = new Transaction(d, "fl")) { t.Start();
 var ft = new FilteredElementCollector(d).OfClass(typeof(FloorType)).Cast<FloorType>().First(); var lv = v == 0 ? l1 : l2;
 double[][] R = { new double[]{0,0,40,26}, new double[]{50,0,30,20}, new double[]{100,5,12,12}, new double[]{0,50,25,8}, new double[]{40,50,10,30}, new double[]{70,50,33,17}, new double[]{110,50,20,40}, new double[]{0,100,15,15}, new double[]{30,100,60,10}, new double[]{100,100,8,22}, new double[]{120,100,45,45}, new double[]{0,130,18,9} };
 foreach (var r in R) { var p = new XYZ[] { new XYZ(r[0], r[1], 0), new XYZ(r[0] + r[2], r[1], 0), new XYZ(r[0] + r[2], r[1] + r[3], 0), new XYZ(r[0], r[1] + r[3], 0) }; var loop = new CurveLoop(); for (int i = 0; i < 4; i++) loop.Append(Line.CreateBound(p[i], p[(i + 1) % 4])); Floor.Create(d, new List<CurveLoop> { loop }, ft.Id, lv.Id); }
 t.Commit(); }
''')

F['params_wall']=("one 10 ft wall on Level 1; base: no custom values; variant: Mark='M-001', Comments='cmt text', and 5 project parameters bound to Walls (instance): RosText='alpha', RosInt=7, RosNum=2.5 (number), RosLen=12 ft (length), RosYN=Yes; values set on the wall",r'''
using (var t = new Transaction(d, "pw")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var w = Wall.Create(d, Line.CreateBound(XYZ.Zero, new XYZ(10, 0, 0)), wt.Id, l1.Id, 10, 0, false, false);
 if (v == 1) {
  w.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("M-001"); w.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set("cmt text");
  string sp = @"C:\wl\out\rosetta_shared.txt"; System.IO.File.WriteAllText(sp, ""); app.SharedParametersFilename = sp; var df = app.OpenSharedParameterFile(); var grp = df.Groups.Create("Rosetta");
  var cats = app.Create.NewCategorySet(); cats.Insert(d.Settings.Categories.get_Item(BuiltInCategory.OST_Walls));
  Func<string, ForgeTypeId, Definition> mk = (nm, ty) => grp.Definitions.Create(new ExternalDefinitionCreationOptions(nm, ty));
  var defs = new Dictionary<string, Definition> { { "RosText", mk("RosText", SpecTypeId.String.Text) }, { "RosInt", mk("RosInt", SpecTypeId.Int.Integer) }, { "RosNum", mk("RosNum", SpecTypeId.Number) }, { "RosLen", mk("RosLen", SpecTypeId.Length) }, { "RosYN", mk("RosYN", SpecTypeId.Boolean.YesNo) } };
  foreach (var kv in defs) d.ParameterBindings.Insert(kv.Value, app.Create.NewInstanceBinding(cats), GroupTypeId.Data);
  d.Regenerate();
  w.LookupParameter("RosText").Set("alpha"); w.LookupParameter("RosInt").Set(7); w.LookupParameter("RosNum").Set(2.5); w.LookupParameter("RosLen").Set(12.0); w.LookupParameter("RosYN").Set(1);
 }
 t.Commit(); }
''')

_LV = r'''
var lvs = new List<Level> { l1 };
using (var t = new Transaction(d, "lv")) { t.Start(); foreach (var z in new double[] { 10, 22, 37 }) { var l = Level.Create(d, z + (v == 1 ? 0.5 : 0)); l.Name = "RC" + (int)z; lvs.Add(l); } t.Commit(); }
d.Regenerate0();
'''.replace("d.Regenerate0();","using (var t = new Transaction(d, \"rg\")) { t.Start(); d.Regenerate(); t.Commit(); }")
F['cols_lv']=("4 new levels RC10 RC22 RC37 (z=10,22,37; variant +0.5) with Level 1 (z=0); 24 structural columns (first symbol) at pseudo-random (x,y) in 0..100 (System.Random seed 7), base level = lvs[i%4], top level = next level (last: RC37 top = RC37+? uses lvs[(i%4)+1] or none -> Level 1 if i%4==3 uses lvs[3] with top offset 10)",_LV+r'''
var rnd = new Random(7);
using (var t = new Transaction(d, "cols")) { t.Start();
 var cs = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_StructuralColumns).Cast<FamilySymbol>().First(); cs.Activate();
 for (int i = 0; i < 24; i++) { double x = Math.Round(rnd.NextDouble() * 100, 3), y = Math.Round(rnd.NextDouble() * 100, 3); int k = i % 4; var lv = lvs[k];
  var c = d.Create.NewFamilyInstance(new XYZ(x, y, lv.Elevation), cs, lv, StructuralType.Column);
  if (k < 3) c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(lvs[k + 1].Id); else c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(lv.Id); if (k == 3) c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).Set(10.0);
  out_ += x + "," + y + "," + k + ";"; }
 t.Commit(); }
''')
F['hosted_lv']=("4 levels as cols_lv; per level k a 40 ft wall from (0,20k) to (40,20k) (Generic first basic type, height = 10) with windows (first Windows symbol) at x=5,15,25,35 sill 2+0.5k, and a door (first Doors symbol) at x=10+k*3",_LV+r'''
using (var t = new Transaction(d, "hl")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var ws = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().First(); ws.Activate();
 var ds = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Doors).Cast<FamilySymbol>().First(); ds.Activate(); d.Regenerate();
 for (int k = 0; k < 4; k++) { var lv = lvs[k]; var w = Wall.Create(d, Line.CreateBound(new XYZ(0, 20 * k, lv.Elevation), new XYZ(40, 20 * k, lv.Elevation)), wt.Id, lv.Id, 10, 0, false, false); d.Regenerate();
  foreach (var x in new double[] { 5, 15, 25, 35 }) d.Create.NewFamilyInstance(new XYZ(x, 20 * k, lv.Elevation + 2 + 0.5 * k), ws, w, lv, StructuralType.NonStructural);
  d.Create.NewFamilyInstance(new XYZ(10 + k * 3, 20 * k, lv.Elevation), ds, w, lv, StructuralType.NonStructural); }
 t.Commit(); }
''')
F['floors_lv']=("4 levels as cols_lv; floor on each level k: rectangle (x0,y0,W,D) = (0,0,30+5k,20+3k) landscape, generic floor type",_LV+r'''
using (var t = new Transaction(d, "fl")) { t.Start(); var ft = new FilteredElementCollector(d).OfClass(typeof(FloorType)).Cast<FloorType>().First();
 for (int k = 0; k < 4; k++) { double W = 30 + 5 * k, D = 20 + 3 * k; var p = new XYZ[] { new XYZ(0, 0, 0), new XYZ(W, 0, 0), new XYZ(W, D, 0), new XYZ(0, D, 0) }; var loop = new CurveLoop(); for (int i = 0; i < 4; i++) loop.Append(Line.CreateBound(p[i], p[(i + 1) % 4])); Floor.Create(d, new List<CurveLoop> { loop }, ft.Id, lvs[k].Id); }
 t.Commit(); }
''')

F['view_sheet']=("one new Level 'RV1' at z=15; base: plan view 'RV1 plan' (first FloorPlan view family type) + 3D view 'RV 3D' (isometric); variant: additionally a sheet 'A-900' named 'Rosetta sheet' (first title block) holding a viewport of the plan at (1,0.7,0)",r'''
using (var t = new Transaction(d, "vs")) { t.Start();
 var lv = Level.Create(d, 15); lv.Name = "RV1";
 var vft = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.FloorPlan);
 var vp = ViewPlan.Create(d, vft.Id, lv.Id); vp.Name = "RV1 plan";
 var v3 = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.ThreeDimensional); var vd = View3D.CreateIsometric(d, v3.Id); vd.Name = "RV 3D";
 if (v == 1) { var tb = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<FamilySymbol>().First(); tb.Activate(); var sh = ViewSheet.Create(d, tb.Id); sh.SheetNumber = "A-900"; sh.Name = "Rosetta sheet"; Viewport.Create(d, sh.Id, vp.Id, new XYZ(1, 0.7, 0)); }
 t.Commit(); }
''')
F['types_door_window']=("duplicate types: base: Doors first symbol duplicated as 'RD 0900x2100' (Width=2.953 ft Height=6.89 ft) and Windows first symbol duplicated as 'RW 1200x1500' (Width 3.937 Height 4.921, Sill 2.953); variant: a third door type 'RD 1000x2400' (3.281 x 7.874) and a column type 'RC 400x600' (b=1.312,h=1.969 if params exist); one instance of each new type placed in a 20 ft wall",r'''
using (var t = new Transaction(d, "tdw")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var w = Wall.Create(d, Line.CreateBound(XYZ.Zero, new XYZ(20, 0, 0)), wt.Id, l1.Id, 10, 0, false, false); d.Regenerate();
 var ds = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Doors).Cast<FamilySymbol>().First();
 var ws = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().First();
 Action<FamilySymbol, double, double> sz = (s, wd, ht) => { foreach (var nm in new[] { "Width", "Height" }) { var p = s.LookupParameter(nm); if (p != null && !p.IsReadOnly) p.Set(nm == "Width" ? wd : ht); } };
 var d1 = ds.Duplicate("RD 0900x2100") as FamilySymbol; sz(d1, 2.953, 6.89); d1.Activate();
 var w1 = ws.Duplicate("RW 1200x1500") as FamilySymbol; sz(w1, 3.937, 4.921); var sl = w1.LookupParameter("Sill Height"); if (sl != null && !sl.IsReadOnly) sl.Set(2.953); w1.Activate(); d.Regenerate();
 d.Create.NewFamilyInstance(new XYZ(5, 0, 0), d1, w, l1, StructuralType.NonStructural); d.Create.NewFamilyInstance(new XYZ(12, 0, 2.953), w1, w, l1, StructuralType.NonStructural);
 if (v == 1) { var d2 = ds.Duplicate("RD 1000x2400") as FamilySymbol; sz(d2, 3.281, 7.874); d2.Activate(); d.Regenerate(); d.Create.NewFamilyInstance(new XYZ(16, 0, 0), d2, w, l1, StructuralType.NonStructural);
  var cs = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_StructuralColumns).Cast<FamilySymbol>().First(); var c1 = cs.Duplicate("RC 400x600") as FamilySymbol; foreach (var nm in new[] { "b", "h", "Width", "Depth" }) { var p = c1.LookupParameter(nm); if (p != null && !p.IsReadOnly && p.StorageType == StorageType.Double) { p.Set(nm == "b" || nm == "Width" ? 1.312 : 1.969); out_ += "set " + nm + ";"; } } c1.Activate(); d.Regenerate(); d.Create.NewFamilyInstance(new XYZ(2, 6, 0), c1, l1, StructuralType.Column); }
 t.Commit(); }
''')

F['all_types']=("one 400 ft wall on Level 1; one instance of EVERY Doors symbol (x=10+20k) and of EVERY Windows symbol (x after doors, sill 3) of the seed in that wall; one column of EVERY structural column symbol at (10k, 20); variant: same but all instances shifted +1 ft in x",r'''
using (var t = new Transaction(d, "at")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var w = Wall.Create(d, Line.CreateBound(XYZ.Zero, new XYZ(400, 0, 0)), wt.Id, l1.Id, 12, 0, false, false); d.Regenerate();
 double sh = v == 1 ? 1 : 0; int k = 0;
 foreach (var s in new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Doors).Cast<FamilySymbol>().OrderBy(x => x.Id.Value).ToList()) { s.Activate(); d.Regenerate(); d.Create.NewFamilyInstance(new XYZ(10 + 12 * k + sh, 0, 0), s, w, l1, StructuralType.NonStructural); out_ += "door:" + s.FamilyName + ":" + s.Name + ";"; k++; }
 foreach (var s in new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().OrderBy(x => x.Id.Value).ToList()) { s.Activate(); d.Regenerate(); d.Create.NewFamilyInstance(new XYZ(10 + 12 * k + sh, 0, 3), s, w, l1, StructuralType.NonStructural); out_ += "win:" + s.FamilyName + ":" + s.Name + ";"; k++; }
 int c = 0; foreach (var s in new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_StructuralColumns).Cast<FamilySymbol>().OrderBy(x => x.Id.Value).ToList()) { s.Activate(); d.Regenerate(); d.Create.NewFamilyInstance(new XYZ(10 * c + sh, 20, 0), s, l1, StructuralType.Column); out_ += "col:" + s.FamilyName + ":" + s.Name + ";"; c++; }
 t.Commit(); }
''')

F['roof_ceiling']=("[SEED = Autodesk Default_M_ENU.rte, not the usual ds0: that template has roof/ceiling types] footprint roof ('Generic Roof - 300mm') over rectangle (0,0)-(30,20) on Level 1 with slope 0 (flat) eave offset 0; and a ceiling (first CeilingType) rectangle (0,0)-(30,20) at Level 1 height offset 9; variant rectangle (0,0)-(34,24) for both",r'''
using (var t = new Transaction(d, "rc")) { t.Start(); double W = v == 0 ? 30 : 34, D = v == 0 ? 20 : 24;
 var rt = new FilteredElementCollector(d).OfClass(typeof(RoofType)).Cast<RoofType>().First(x => x.Name.StartsWith("Generic Roof - 300"));
 var ca = new CurveArray(); var p = new XYZ[] { new XYZ(0,0,0), new XYZ(W,0,0), new XYZ(W,D,0), new XYZ(0,D,0) }; for (int i = 0; i < 4; i++) ca.Append(Line.CreateBound(p[i], p[(i+1)%4]));
 ModelCurveArray mca = new ModelCurveArray(); var roof = d.Create.NewFootPrintRoof(ca, l1, rt, out mca); foreach (ModelCurve mc in mca) roof.set_DefinesSlope(mc, false);
 var ct = new FilteredElementCollector(d).OfClass(typeof(CeilingType)).Cast<CeilingType>().First(); var loop = new CurveLoop(); for (int i = 0; i < 4; i++) loop.Append(Line.CreateBound(p[i], p[(i+1)%4]));
 var ce = Ceiling.Create(d, new List<CurveLoop> { loop }, ct.Id, l1.Id); ce.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM).Set(9.0);
 t.Commit(); }
''')

F['roofs12']=("[SEED = <year>_house_base.rte] RoofType 'Generic Roof - 300mm' + first CeilingType copied from Default_M_ENU.rte (ElementTransformUtils.CopyElements, separate transaction), then 12 flat footprint roofs and 12 ceilings (height offset 9) over rectangles R[k] (W>=D) on Level 1; variant: same on a new level 'RF' z=12",r'''
var src = app.OpenDocumentFile(@"C:\ProgramData\Autodesk\RVT __Y__\Templates\Default_M_ENU.rte");
var srt = new FilteredElementCollector(src).OfClass(typeof(RoofType)).Cast<RoofType>().First(x => x.Name.StartsWith("Generic Roof - 300"));
var sct = new FilteredElementCollector(src).OfClass(typeof(CeilingType)).Cast<CeilingType>().First();
ICollection<ElementId> cp; using (var t = new Transaction(d, "cp")) { t.Start(); cp = ElementTransformUtils.CopyElements(src, new List<ElementId> { srt.Id }, d, Transform.Identity, new CopyPasteOptions()); cp = cp.Concat(ElementTransformUtils.CopyElements(src, new List<ElementId> { sct.Id }, d, Transform.Identity, new CopyPasteOptions())).ToList(); t.Commit(); }
src.Close(false); out_ += "copied=" + string.Join(",", cp.Select(x => x.ToString()));
double[][] R = { new double[]{60,-100,40,26}, new double[]{110,-100,30,20}, new double[]{150,-100,24,24}, new double[]{60,-150,50,10}, new double[]{120,-150,36,18}, new double[]{170,-150,20,12}, new double[]{60,-200,44,30}, new double[]{115,-200,28,27}, new double[]{150,-200,60,15}, new double[]{220,-200,18,9}, new double[]{220,-100,33,21}, new double[]{220,-150,26,13} };
Level lr = l1; if (v == 1) { using (var t = new Transaction(d, "lv")) { t.Start(); lr = Level.Create(d, 12); lr.Name = "RF"; t.Commit(); } }
using (var t = new Transaction(d, "rf")) { t.Start(); var rt = d.GetElement(cp.First(x => d.GetElement(x) is RoofType)) as RoofType; var ct = d.GetElement(cp.First(x => d.GetElement(x) is CeilingType)) as CeilingType;
 for (int k = 0; k < 12; k++) { double x0 = R[k][0], y0 = R[k][1], W = R[k][2], D = R[k][3], z = lr.Elevation; var p = new XYZ[] { new XYZ(x0,y0,z), new XYZ(x0+W,y0,z), new XYZ(x0+W,y0+D,z), new XYZ(x0,y0+D,z) };
  var ca = new CurveArray(); for (int i = 0; i < 4; i++) ca.Append(Line.CreateBound(p[i], p[(i+1)%4])); ModelCurveArray mca = new ModelCurveArray(); var roof = d.Create.NewFootPrintRoof(ca, lr, rt, out mca); foreach (ModelCurve mc in mca) roof.set_DefinesSlope(mc, false);
  var loop = new CurveLoop(); for (int i = 0; i < 4; i++) loop.Append(Line.CreateBound(p[i], p[(i+1)%4])); var ce = Ceiling.Create(d, new List<CurveLoop> { loop }, ct.Id, lr.Id); ce.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM).Set(9.0);
  out_ += " R" + k + "=" + roof.Id + "/" + ce.Id; }
 t.Commit(); }
''')
# ---------------- SHIFT rosetta (seed = <year>_house_base.rte): one Revit-made object; variant = the same object translated by (+100,+50,0). The writer places translated copies (genlib2.GroupShiftTpl) ----------------
F['stair_shift']=("[SEED house_base] straight stair Level 1 -> Level 2, run (60,40)-(75,40) justification Center (its auto railings included); variant translated (+100,+50)",r'''
double DX = v == 1 ? 100 : 0, DY = v == 1 ? 50 : 0;
var scope = new StairsEditScope(d, "stairs"); ElementId sid = scope.Start(l1.Id, l2.Id);
using (var t = new Transaction(d, "run")) { t.Start(); StairsRun.CreateStraightRun(d, sid, Line.CreateBound(new XYZ(60+DX,40+DY,0), new XYZ(75+DX,40+DY,0)), StairsRunJustification.Center); t.Commit(); }
scope.Commit(new StairsFailurePreprocessor()); out_ += "stair=" + sid;
''')
F['railing_shift']=("[SEED house_base] railing on Level 1 along (60,50)-(80,50)-(80,58), first RailingType; variant translated (+100,+50)",r'''
double DX = v == 1 ? 100 : 0, DY = v == 1 ? 50 : 0;
using (var t = new Transaction(d, "r")) { t.Start(); var rt = new FilteredElementCollector(d).OfClass(typeof(RailingType)).FirstElement().Id;
 var loop = new CurveLoop(); loop.Append(Line.CreateBound(new XYZ(60+DX,50+DY,0), new XYZ(80+DX,50+DY,0))); loop.Append(Line.CreateBound(new XYZ(80+DX,50+DY,0), new XYZ(80+DX,58+DY,0))); var r = Railing.Create(d, loop, rt, l1.Id); t.Commit(); out_ += "railing=" + r.Id; }
''')
F['curtain_shift']=("[SEED house_base] curtain wall (first Curtain WallType, type NOT modified) (60,62)-(84,62) height 12 on Level 1, grid lines u at x=66,72,78 and v at z=4,8, mullions (first MullionType) on every grid segment; variant translated (+100,+50)",r'''
double DX = v == 1 ? 100 : 0, DY = v == 1 ? 50 : 0;
using (var t = new Transaction(d, "cw")) { t.Start();
 var cwt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Curtain);
 var w = Wall.Create(d, Line.CreateBound(new XYZ(60+DX,62+DY,0), new XYZ(84+DX,62+DY,0)), cwt.Id, l1.Id, 12, 0, false, false); d.Regenerate();
 var mt = new FilteredElementCollector(d).OfClass(typeof(MullionType)).Cast<MullionType>().First(); var cg = w.CurtainGrid; var gl = new List<CurtainGridLine>();
 foreach (var x in new double[] { 66, 72, 78 }) gl.Add(cg.AddGridLine(false, new XYZ(x+DX, 62+DY, 0), false));
 foreach (var z in new double[] { 4, 8 }) gl.Add(cg.AddGridLine(true, new XYZ(60+DX, 62+DY, z), false));
 d.Regenerate(); int nm = 0; foreach (var g in gl) foreach (Curve c in g.AllSegmentCurves) { try { g.AddMullions(c, mt, false); nm++; } catch { } }
 t.Commit(); out_ += "cw=" + w.Id + " mullions=" + nm; }
''')
F['roof_shift']=("[SEED house_base] RoofType 'Generic Roof - 300mm' + first CeilingType copied from Default_M_ENU.rte (types are part of both base and var, identical); flat footprint roof over (60,-100)-(90,-80) on Level 1 + ceiling (height offset 9) same rectangle; variant translated (+100,+50)",r'''
double DX = v == 1 ? 100 : 0, DY = v == 1 ? 50 : 0;
var src = app.OpenDocumentFile(@"C:\ProgramData\Autodesk\RVT __Y__\Templates\Default_M_ENU.rte");
var srt = new FilteredElementCollector(src).OfClass(typeof(RoofType)).Cast<RoofType>().First(x => x.Name.StartsWith("Generic Roof - 300"));
var sct = new FilteredElementCollector(src).OfClass(typeof(CeilingType)).Cast<CeilingType>().First();
ICollection<ElementId> cp; using (var t = new Transaction(d, "cp")) { t.Start(); cp = ElementTransformUtils.CopyElements(src, new List<ElementId> { srt.Id }, d, Transform.Identity, new CopyPasteOptions()); cp = cp.Concat(ElementTransformUtils.CopyElements(src, new List<ElementId> { sct.Id }, d, Transform.Identity, new CopyPasteOptions())).ToList(); t.Commit(); }
src.Close(false); out_ += "copied=" + string.Join(",", cp.Select(x => x.ToString()));
using (var t = new Transaction(d, "rf")) { t.Start(); var rt = d.GetElement(cp.First(x => d.GetElement(x) is RoofType)) as RoofType; var ct = d.GetElement(cp.First(x => d.GetElement(x) is CeilingType)) as CeilingType;
 double x0 = 60 + DX, y0 = -100 + DY, W = 30, D = 20, z = l1.Elevation; var p = new XYZ[] { new XYZ(x0,y0,z), new XYZ(x0+W,y0,z), new XYZ(x0+W,y0+D,z), new XYZ(x0,y0+D,z) };
 var ca = new CurveArray(); for (int i = 0; i < 4; i++) ca.Append(Line.CreateBound(p[i], p[(i+1)%4])); ModelCurveArray mca = new ModelCurveArray(); var roof = d.Create.NewFootPrintRoof(ca, l1, rt, out mca); foreach (ModelCurve mc in mca) roof.set_DefinesSlope(mc, false);
 var loop = new CurveLoop(); for (int i = 0; i < 4; i++) loop.Append(Line.CreateBound(p[i], p[(i+1)%4])); var ce = Ceiling.Create(d, new List<CurveLoop> { loop }, ct.Id, l1.Id); ce.get_Parameter(BuiltInParameter.CEILING_HEIGHTABOVELEVEL_PARAM).Set(9.0);
 t.Commit(); out_ += " roof=" + roof.Id + " ceiling=" + ce.Id; }
''')
F['grid_house']=("[SEED house_base] ONE grid G2 (10,-5)-(10,25); variant: none (base = house_base + grid, var = same grid translated +100,+50 is NOT used); used to see what Revit changes in a house when a grid is added",r'''
double DX = v == 1 ? 100 : 0, DY = v == 1 ? 50 : 0;
using (var t = new Transaction(d, "g")) { t.Start(); var g = Grid.Create(d, Line.CreateBound(new XYZ(10+DX,-5+DY,0), new XYZ(10+DX,25+DY,0))); g.Name = "G2"; t.Commit(); out_ += "grid=" + g.Id; }
''')
F['rooms_lv']=("8 new levels (z=10*k+10); on each level k one rectangular room bounded by 4 generic walls (height 9): rectangle (x0,y0,W,D) = (0,0,20,12) (5,5,14,9) (10,0,25,10) (0,8,16,16) (30,30,12,8) (2,2,30,12) (0,0,11,7) (20,10,18,13); room at the centre named 'RR<k>' number '<k>'; variant: rectangles shifted by +3 in x",r'''
double[][] R = { new double[]{0,0,20,12}, new double[]{5,5,14,9}, new double[]{10,0,25,10}, new double[]{0,8,16,16}, new double[]{30,30,12,8}, new double[]{2,2,30,12}, new double[]{0,0,11,7}, new double[]{20,10,18,13} };
var lv = new List<Level>(); using (var t = new Transaction(d, "lv")) { t.Start(); for (int k = 0; k < 8; k++) { var l = Level.Create(d, 10 * k + 10); l.Name = "RM" + k; lv.Add(l); } t.Commit(); }
using (var t = new Transaction(d, "rg")) { t.Start(); d.Regenerate(); t.Commit(); }
using (var t = new Transaction(d, "rm")) { t.Start(); var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 for (int k = 0; k < 8; k++) { double x0 = R[k][0] + (v == 1 ? 3 : 0), y0 = R[k][1], W = R[k][2], D = R[k][3]; var p = new XYZ[] { new XYZ(x0, y0, 0), new XYZ(x0 + W, y0, 0), new XYZ(x0 + W, y0 + D, 0), new XYZ(x0, y0 + D, 0) };
  for (int i = 0; i < 4; i++) { var l = Line.CreateBound(new XYZ(p[i].X, p[i].Y, lv[k].Elevation), new XYZ(p[(i+1)%4].X, p[(i+1)%4].Y, lv[k].Elevation)); Wall.Create(d, l, wt.Id, lv[k].Id, 9, 0, false, false); } }
 t.Commit(); }
using (var t = new Transaction(d, "rg2")) { t.Start(); d.Regenerate(); t.Commit(); }
using (var t = new Transaction(d, "rm2")) { t.Start(); for (int k = 0; k < 8; k++) { double x0 = R[k][0] + (v == 1 ? 3 : 0); var r = d.Create.NewRoom(lv[k], new UV(x0 + R[k][2] / 2, R[k][1] + R[k][3] / 2)); r.Name = "RR" + k; r.Number = "" + k; out_ += "room " + k + " area " + r.Area + ";"; } t.Commit(); }
''')

F['walls_open_k']=("12 walls 60 ft along x at y=20*i (i=0..11) on Level 1 (Generic basic type, height 10); wall i has k=1+(i%4) windows (first Windows symbol, sill 3) at x = 5 + 12*j + (i//4)*3 + (i%4)*0.5 for j<k; variant: windows shifted +1 ft",r'''
using (var t = new Transaction(d, "wk")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var ws = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().First(); ws.Activate(); d.Regenerate();
 for (int i = 0; i < 12; i++) { var w = Wall.Create(d, Line.CreateBound(new XYZ(0, 20 * i, 0), new XYZ(60, 20 * i, 0)), wt.Id, l1.Id, 10, 0, false, false); d.Regenerate(); int k = 1 + (i % 4);
  for (int j = 0; j < k; j++) { double x = 5 + 12 * j + (i / 4) * 3 + (i % 4) * 0.5 + (v == 1 ? 1 : 0); d.Create.NewFamilyInstance(new XYZ(x, 20 * i, 3), ws, w, l1, StructuralType.NonStructural); } }
 t.Commit(); }
''')

F['walls_open_k2']=("24 walls 60 ft along x at y=20*i on Level 1 (generic basic, height 10); wall i has k=1+(i%4) windows (first Windows symbol, sill 3) at distinct pseudo-random x (System.Random(11), spaced >=8 ft apart, 4..56) sorted ascending; variant: all windows +0.75 ft",r'''
using (var t = new Transaction(d, "wk2")) { t.Start(); var rnd = new Random(11);
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var ws = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().First(); ws.Activate(); d.Regenerate();
 for (int i = 0; i < 24; i++) { var w = Wall.Create(d, Line.CreateBound(new XYZ(0, 20 * i, 0), new XYZ(60, 20 * i, 0)), wt.Id, l1.Id, 10, 0, false, false); d.Regenerate(); int k = 1 + (i % 4);
  var xs = new List<double>(); while (xs.Count < k) { double x = Math.Round(4 + rnd.NextDouble() * 52, 2); if (xs.All(q => Math.Abs(q - x) >= 8)) xs.Add(x); } xs.Sort();
  foreach (var x in xs) { d.Create.NewFamilyInstance(new XYZ(x + (v == 1 ? 0.75 : 0), 20 * i, 3), ws, w, l1, StructuralType.NonStructural); } }
 t.Commit(); }
''')

F['walls_open_geom']=("24 walls with exactly ONE window (first Windows symbol, sill 3) at relative position 0.4 of the wall: wall i: dir = [+x,+y,-x,-y][i%4], start (50*(i//4), 30*(i//4)), length L = [30,45,60,75,90,40][i//4], height H = [10,12,9,14,10,11][i//4] on Level 1; variant: windows at relative position 0.6",r'''
using (var t = new Transaction(d, "wg")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var ws = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().First(); ws.Activate(); d.Regenerate();
 double[] Ls = { 30, 45, 60, 75, 90, 40 }, Hs = { 10, 12, 9, 14, 10, 11 }; double[][] dirs = { new double[]{1,0}, new double[]{0,1}, new double[]{-1,0}, new double[]{0,-1} };
 for (int i = 0; i < 24; i++) { int g = i / 4, q = i % 4; double L = Ls[g], H = Hs[g]; double sx = 200 * g + (q == 2 ? L : 0) + 20 * q, sy = 150 * g + (q == 3 ? L : 0) + 100 * q + 5 * g;
  var p0 = new XYZ(sx, sy, 0); var p1 = new XYZ(sx + dirs[q][0] * L, sy + dirs[q][1] * L, 0);
  var w = Wall.Create(d, Line.CreateBound(p0, p1), wt.Id, l1.Id, H, 0, false, false); d.Regenerate();
  double f = v == 0 ? 0.4 : 0.6; var pos = p0 + (p1 - p0) * f; d.Create.NewFamilyInstance(new XYZ(pos.X, pos.Y, 3), ws, w, l1, StructuralType.NonStructural); out_ += i + ":" + sx + "," + sy + ";"; }
 t.Commit(); }
''')

F['walls_open_geom2']=("24 walls near the origin (all points within 60 ft), exactly ONE window at relative position f (base 0.4, variant 0.6): wall i: dir=[+x,+y,-x,-y][i%4], k=i//4 in 0..5: length L=[20,26,32,38,44,30][k], height H=[10,12,9,14,11,13][k], start offsets so that the wall lies in the box [-40,40]^2: start = (-15+7*k - (dir==-x?0:0), -10+5*k) shifted per direction by 12*dirIndex in the perpendicular axis",r'''
using (var t = new Transaction(d, "wg2")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var ws = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().First(); ws.Activate(); d.Regenerate();
 double[] Ls = { 20, 26, 32, 38, 44, 30 }, Hs = { 10, 12, 9, 14, 11, 13 }; double[][] dirs = { new double[]{1,0}, new double[]{0,1}, new double[]{-1,0}, new double[]{0,-1} };
 for (int i = 0; i < 24; i++) { int q = i % 4, k = i / 4; double L = Ls[k], H = Hs[k];
  double sx = -15 + 7 * k + (q == 2 ? L : 0) + (q == 1 ? 12 : 0) - (q == 3 ? 12 : 0), sy = -10 + 5 * k + (q == 3 ? L : 0) + (q == 0 ? -12 : 0) + (q == 2 ? 12 : 0);
  var p0 = new XYZ(sx, sy, 0); var p1 = new XYZ(sx + dirs[q][0] * L, sy + dirs[q][1] * L, 0);
  var w = Wall.Create(d, Line.CreateBound(p0, p1), wt.Id, l1.Id, H, 0, false, false); d.Regenerate();
  double f = v == 0 ? 0.4 : 0.6; var pos = p0 + (p1 - p0) * f; d.Create.NewFamilyInstance(new XYZ(pos.X, pos.Y, 3), ws, w, l1, StructuralType.NonStructural); out_ += i + ":" + sx + "," + sy + ";"; }
 t.Commit(); }
''')

F['topography_shift']=("same 5-point surface as 'topography' (corners (0,0,0),(40,0,2),(40,40,4),(0,40,2), centre (20,20,5)) translated by (+100,+50) in the variant (same z)",r'''
using (var t = new Transaction(d, "ts")) { t.Start(); double dx = v == 1 ? 100 : 0, dy = v == 1 ? 50 : 0; var pts = new List<XYZ> { new XYZ(dx, dy, 0), new XYZ(40 + dx, dy, 2), new XYZ(40 + dx, 40 + dy, 4), new XYZ(dx, 40 + dy, 2), new XYZ(20 + dx, 20 + dy, 5) }; TopographySurface.Create(d, pts); t.Commit(); }
''')

F['sheet_viewport']=("new Level 'RS1' z=15 with plan view 'RS1 plan' and a sheet 'A-910' 'Viewport sheet' (first title block); base: sheet WITHOUT viewport; variant: the plan placed on the sheet as a viewport at (1.0,0.7,0)",r'''
using (var t = new Transaction(d, "sv")) { t.Start();
 var lv = Level.Create(d, 15); lv.Name = "RS1";
 var vft = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.FloorPlan);
 var vp = ViewPlan.Create(d, vft.Id, lv.Id); vp.Name = "RS1 plan";
 var tb = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<FamilySymbol>().First(); tb.Activate(); var sh = ViewSheet.Create(d, tb.Id); sh.SheetNumber = "A-910"; sh.Name = "Viewport sheet";
 if (v == 1) { Viewport.Create(d, sh.Id, vp.Id, new XYZ(1, 0.7, 0)); }
 t.Commit(); }
''')
F['sheet_viewport_pos']=("as sheet_viewport variant (plan placed on sheet 'A-911'); base: viewport centre (1.0,0.7,0); variant: (1.4,0.9,0)",r'''
using (var t = new Transaction(d, "svp")) { t.Start();
 var lv = Level.Create(d, 15); lv.Name = "RS2";
 var vft = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.FloorPlan);
 var vp = ViewPlan.Create(d, vft.Id, lv.Id); vp.Name = "RS2 plan";
 var tb = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<FamilySymbol>().First(); tb.Activate(); var sh = ViewSheet.Create(d, tb.Id); sh.SheetNumber = "A-911"; sh.Name = "Viewport pos sheet";
 Viewport.Create(d, sh.Id, vp.Id, v == 0 ? new XYZ(1.0, 0.7, 0) : new XYZ(1.4, 0.9, 0));
 t.Commit(); }
''')

F['sheet_viewport2']=("2024 retry of sheet_viewport (first run saved no viewport): level 'RS3' z=15, plan 'RS3 plan', sheet 'A-912'; view+sheet committed in a first transaction, then (variant only) Viewport.Create at (1.0,0.7,0) in a second transaction; out reports CanAddViewToSheet and the new id",r'''
ViewPlan vp = null; ViewSheet sh = null;
using (var t = new Transaction(d, "sv2a")) { t.Start();
 var lv = Level.Create(d, 15); lv.Name = "RS3";
 var vft = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.FloorPlan);
 vp = ViewPlan.Create(d, vft.Id, lv.Id); vp.Name = "RS3 plan";
 var tb = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<FamilySymbol>().First(); tb.Activate(); sh = ViewSheet.Create(d, tb.Id); sh.SheetNumber = "A-912"; sh.Name = "Viewport sheet 2";
 t.Commit(); }
if (v == 1) { using (var t = new Transaction(d, "sv2b")) { t.Start(); d.Regenerate(); out_ += "can=" + Viewport.CanAddViewToSheet(d, sh.Id, vp.Id); var x = Viewport.Create(d, sh.Id, vp.Id, new XYZ(1.0, 0.7, 0));
 if (x == null) { out_ += " try2:"; var dl = d.Create.NewDetailCurve(vp, Line.CreateBound(new XYZ(0,0,15), new XYZ(10,0,15))); d.Regenerate(); x = Viewport.Create(d, sh.Id, vp.Id, new XYZ(1.0, 0.7, 0)); }
 if (x == null) { out_ += " try3:"; try { var es = d.GetElement(sh.GetAllPlacedViews().FirstOrDefault()); out_ += "placed0=" + (es == null ? "none" : es.Name); } catch (Exception ex) { out_ += ex.Message; } } out_ += " vp=" + (x == null ? "null" : x.Id.ToString()); var r = t.Commit(); out_ += " commit=" + r; } out_ += " placed=" + vp.get_Parameter(BuiltInParameter.VIEWPORT_SHEET_NUMBER).AsString(); }
''')

# ---------------- view/sheet rosetta (requester: rvt-sheets). Common base scene; exactly ONE change in the variant ----------------
_VB = r'''
Level vl = null; ViewPlan vp = null; ViewSheet sh = null; Viewport vpt = null; Wall w0 = null; FamilyInstance door0 = null;
using (var t = new Transaction(d, "vbase")) { t.Start();
 vl = Level.Create(d, 20); vl.Name = "VR1";
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var p = new XYZ[] { new XYZ(0, 0, 20), new XYZ(20, 0, 20), new XYZ(20, 14, 20), new XYZ(0, 14, 20) };
 var ws = new List<Wall>(); for (int i = 0; i < 4; i++) { var w = Wall.Create(d, Line.CreateBound(p[i], p[(i + 1) % 4]), wt.Id, vl.Id, 9, 0, false, false); w.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set(i == 0 ? "A" : "B"); ws.Add(w); }
 w0 = ws[0]; d.Regenerate();
 var ds = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Doors).Cast<FamilySymbol>().First(); ds.Activate();
 var wn = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_Windows).Cast<FamilySymbol>().First(); wn.Activate(); d.Regenerate();
 door0 = d.Create.NewFamilyInstance(new XYZ(6, 0, 20), ds, w0, vl, StructuralType.NonStructural); d.Create.NewFamilyInstance(new XYZ(20, 7, 23), wn, ws[1], vl, StructuralType.NonStructural);
 var ft = new FilteredElementCollector(d).OfClass(typeof(FloorType)).Cast<FloorType>().First(); var loop = new CurveLoop(); for (int i = 0; i < 4; i++) loop.Append(Line.CreateBound(new XYZ(p[i].X, p[i].Y, 0), new XYZ(p[(i + 1) % 4].X, p[(i + 1) % 4].Y, 0))); Floor.Create(d, new List<CurveLoop> { loop }, ft.Id, vl.Id);
 var vft = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.FloorPlan);
 vp = ViewPlan.Create(d, vft.Id, vl.Id); vp.Name = "VR plan"; vp.Scale = 100; vp.DetailLevel = ViewDetailLevel.Coarse;
 var pvr = vp.GetViewRange(); pvr.SetOffset(PlanViewPlane.CutPlane, 4.0); vp.SetViewRange(pvr);
 var tb = new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).OfCategory(BuiltInCategory.OST_TitleBlocks).Cast<FamilySymbol>().First(); tb.Activate();
 sh = ViewSheet.Create(d, tb.Id); sh.SheetNumber = "V-100"; sh.Name = "View rosetta sheet";
 vpt = Viewport.Create(d, sh.Id, vp.Id, new XYZ(1.0, 0.7, 0));
 t.Commit(); }
if (v == 1) { using (var t = new Transaction(d, "vvar")) { t.Start(); __VAR__ t.Commit(); } }
'''
def _vf(desc, var): F_ = (desc, _VB.replace('__VAR__', var)); return F_
F['view_a_viewport_move']=_vf("plan 'VR plan' (level VR1 z=20; 4 walls 20x14, Mark A on the first wall, door, window, floor) on sheet 'V-100' with a title block, viewport centre (1.0,0.7,0); scale 1:100, Coarse, cut plane +4.0 ft. VARIANT (a): viewport moved to centre (1.1,0.75,0)","vpt.SetBoxCenter(new XYZ(1.1, 0.75, 0));")
F['view_b_scale']=_vf("(b) base scale 1:100 -> variant 1:50","vp.Scale = 50;")
F['view_c_crop']=_vf("(c) base crop off -> variant crop on and shrunk by (3,2) ft from min corner","vp.CropBoxActive = true; var bb = vp.CropBox; bb.Min = new XYZ(bb.Min.X + 3, bb.Min.Y + 2, bb.Min.Z); vp.CropBox = bb; vp.CropBoxVisible = true;")
F['view_d_range']=_vf("(d) cut plane offset 4.0 ft -> 3.0 ft","var pv2 = vp.GetViewRange(); pv2.SetOffset(PlanViewPlane.CutPlane, 3.0); vp.SetViewRange(pv2);")
F['view_e_category']=_vf("(e) Walls category override: projection line weight 5, colour red (255,0,0)","var og = new OverrideGraphicSettings(); og.SetProjectionLineWeight(5); og.SetProjectionLineColor(new Color(255, 0, 0)); vp.SetCategoryOverrides(new ElementId(BuiltInCategory.OST_Walls), og);")
F['view_f_filter']=_vf("(f) ParameterFilterElement 'Mark is A' on Walls (rule: Mark equals \"A\") added to the view with cut foreground pattern <Solid fill> (colour blue 0,0,255) and halftone","var cats = new List<ElementId> { new ElementId(BuiltInCategory.OST_Walls) }; var rule = ParameterFilterRuleFactory.CreateEqualsRule(new ElementId(BuiltInParameter.ALL_MODEL_MARK), \"A\"); var pfe = ParameterFilterElement.Create(d, \"Mark is A\", cats, new ElementParameterFilter(rule)); vp.AddFilter(pfe.Id); var og2 = new OverrideGraphicSettings(); var sf = FillPatternElement.GetFillPatternElementByName(d, FillPatternTarget.Drafting, \"<Solid fill>\"); og2.SetCutForegroundPatternId(sf.Id); og2.SetCutForegroundPatternColor(new Color(0, 0, 255)); og2.SetHalftone(true); vp.SetFilterOverrides(pfe.Id, og2);")
F['view_g_element']=_vf("(g) element override on the first wall (Mark A): surface transparency 50, halftone","var og3 = new OverrideGraphicSettings(); og3.SetSurfaceTransparency(50); og3.SetHalftone(true); vp.SetElementOverrides(w0.Id, og3);")
F['view_h_template']=_vf("(h) view template assigned: first plan view template in the project (name recorded in out)","var tpl = new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<ViewPlan>().First(x => x.IsTemplate); vp.ViewTemplateId = tpl.Id; out_ += \"template=\" + tpl.Name + \";\";")
F['view_i_detail']=_vf("(i) detail level Coarse -> Fine","vp.DetailLevel = ViewDetailLevel.Fine;")
F['view_j_phasefilter']=_vf("(j) phase filter 'Show New' set on the view (VIEW_PHASE_FILTER)","var pfx = new FilteredElementCollector(d).OfClass(typeof(PhaseFilter)).Cast<PhaseFilter>().First(x => x.Name == \"Show New\"); vp.get_Parameter(BuiltInParameter.VIEW_PHASE_FILTER).Set(pfx.Id);")
F['view_k_annotations']=_vf("(k) added to the view: TextNote 'Note A' at (5,5), linear Dimension between the interior faces of the two vertical walls (x=0 and x=20) at y=7, detail line (1,1)-(9,1), filled region 3x2 at (14,9) (each in its own try; failures reported in out)","""
 try { var tnt = new FilteredElementCollector(d).OfClass(typeof(TextNoteType)).FirstElement().Id; TextNote.Create(d, vp.Id, new XYZ(5, 5, 20), "Note A", tnt); out_ += "text ok;"; } catch (Exception ex) { out_ += "textERR " + ex.Message.Split('\\n')[0] + ";"; }
 try { var vw = new FilteredElementCollector(d).OfClass(typeof(Wall)).Cast<Wall>().Where(x => x.LevelId == vl.Id).Where(x => { var c = (x.Location as LocationCurve).Curve; return Math.Abs(c.GetEndPoint(0).X - c.GetEndPoint(1).X) < 0.01; }).OrderBy(x => (x.Location as LocationCurve).Curve.GetEndPoint(0).X).ToList(); var ra = new ReferenceArray(); ra.Append(HostObjectUtils.GetSideFaces(vw.First(), ShellLayerType.Interior)[0]); ra.Append(HostObjectUtils.GetSideFaces(vw.Last(), ShellLayerType.Interior)[0]); d.Create.NewDimension(vp, Line.CreateBound(new XYZ(0, 7, 20), new XYZ(20, 7, 20)), ra); out_ += "dim ok;"; } catch (Exception ex) { out_ += "dimERR " + ex.Message.Split((char)10)[0] + ";"; }
 try { d.Create.NewDetailCurve(vp, Line.CreateBound(new XYZ(1, 1, 20), new XYZ(9, 1, 20))); out_ += "detail ok;"; } catch (Exception ex) { out_ += "detailERR " + ex.Message.Split('\\n')[0] + ";"; }
 try { var frt = new FilteredElementCollector(d).OfClass(typeof(FilledRegionType)).FirstElement().Id; var lp = new CurveLoop(); var q = new XYZ[] { new XYZ(14, 9, 20), new XYZ(17, 9, 20), new XYZ(17, 11, 20), new XYZ(14, 11, 20) }; for (int i = 0; i < 4; i++) lp.Append(Line.CreateBound(q[i], q[(i + 1) % 4])); FilledRegion.Create(d, frt, vp.Id, new List<CurveLoop> { lp }); out_ += "region ok;"; } catch (Exception ex) { out_ += "regionERR " + ex.Message.Split('\\n')[0] + ";"; }
""")
F['view_l_section_schedule']=_vf("(l) second viewport on the sheet: a section view through the model (section box 20 wide) placed at (1.0,0.3) + a wall schedule instance placed on the sheet at (0.2,0.9)","""
 try { var sft = new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.Section); var tr = Transform.Identity; tr.Origin = new XYZ(10, -2, 24); tr.BasisX = XYZ.BasisX; tr.BasisY = XYZ.BasisZ; tr.BasisZ = -XYZ.BasisY; var bx = new BoundingBoxXYZ { Transform = tr, Min = new XYZ(-12, -6, 0), Max = new XYZ(12, 6, 8) }; var sec = ViewSection.CreateSection(d, sft.Id, bx); sec.Name = "VR section"; Viewport.Create(d, sh.Id, sec.Id, new XYZ(1.0, 0.3, 0)); out_ += "section ok;"; } catch (Exception ex) { out_ += "secERR " + ex.Message.Split('\\n')[0] + ";"; }
 try { var sched = ViewSchedule.CreateSchedule(d, new ElementId(BuiltInCategory.OST_Walls)); sched.Name = "VR wall schedule"; ScheduleSheetInstance.Create(d, sh.Id, sched.Id, new XYZ(0.2, 0.9, 0)); out_ += "sched ok;"; } catch (Exception ex) { out_ += "schedERR " + ex.Message.Split('\\n')[0] + ";"; }
""")

# ---- complex generative forms (2026-10-15, c4-writer): partial revolves, curved/3D sweeps, blends with arcs/twist, swept blends, voids from them
_CIRC = lambda c, r, z='0': 'new Func<XYZ,double,CurveArray>((c_, r_) => { var a_ = new CurveArray(); a_.Append(Arc.Create(c_, r_, 0, Math.PI, XYZ.BasisX, XYZ.BasisY)); a_.Append(Arc.Create(c_, r_, Math.PI, 2*Math.PI, XYZ.BasisX, XYZ.BasisY)); return a_; })'
_HELP = r'''
 Func<XYZ, double, CurveArray> circ = (c_, r_) => { var a_ = new CurveArray(); a_.Append(Arc.Create(c_, r_, 0, Math.PI, XYZ.BasisX, XYZ.BasisY)); a_.Append(Arc.Create(c_, r_, Math.PI, 2*Math.PI, XYZ.BasisX, XYZ.BasisY)); return a_; };
 Func<double, double, double, double, double, CurveArray> rect = (x0, y0, x1, y1, z) => { var a_ = new CurveArray(); var q = new XYZ[] { new XYZ(x0,y0,z), new XYZ(x1,y0,z), new XYZ(x1,y1,z), new XYZ(x0,y1,z) }; for (int i = 0; i < 4; i++) a_.Append(Line.CreateBound(q[i], q[(i+1)%4])); return a_; };
 Func<CurveArray, CurveArrArray> one = (ca_) => { var c2 = new CurveArrArray(); c2.Append(ca_); return c2; };
'''
F['fam_revolve_partial']=famfeat("revolve of rectangle x 1..2, z 0..2 around the Z axis through 90 degrees (variant 200 degrees): partial revolve with planar faces at both ends",_HELP+r'''
 double ang = v==0 ? Math.PI/2 : 200*Math.PI/180;
 var prof = new CurveArray(); var q = new XYZ[] { new XYZ(1,0,0), new XYZ(2,0,0), new XYZ(2,0,2), new XYZ(1,0,2) }; for (int i = 0; i < 4; i++) prof.Append(Line.CreateBound(q[i], q[(i+1)%4]));
 fd.FamilyCreate.NewRevolution(true, one(prof), spx, Line.CreateBound(new XYZ(0,0,0), new XYZ(0,0,1)), 0, ang);''')
F['fam_revolve_arc_spline']=famfeat("revolve 270 degrees (variant 180) of a profile bounded by the axis, a base line, an outer ARC and an inner HERMITE SPLINE: vase-like body of revolution with cylindrical/toroidal and spline-of-revolution faces",_HELP+r'''
 double ang = v==0 ? 1.5*Math.PI : Math.PI;
 var prof = new CurveArray(); prof.Append(Line.CreateBound(new XYZ(0,0,0), new XYZ(2,0,0)));
 prof.Append(Arc.Create(new XYZ(2,0,0), new XYZ(2,0,2), new XYZ(2.5,0,1)));
 prof.Append(HermiteSpline.Create(new List<XYZ> { new XYZ(2,0,2), new XYZ(1.2,0,3), new XYZ(0.6,0,4.5), new XYZ(0,0,5) }, false));
 prof.Append(Line.CreateBound(new XYZ(0,0,5), new XYZ(0,0,0)));
 fd.FamilyCreate.NewRevolution(true, one(prof), spx, Line.CreateBound(new XYZ(0,0,0), new XYZ(0,0,1)), 0, ang);''')
F['fam_sweep_line_arc_line']=famfeat("sweep of an L-shaped profile with a rounded corner along a path line(3)+arc(r=2, 90deg)+line(3) in the XZ plane, tangent continuous (variant arc radius 3)",_HELP+r'''
 double R = v==0?2:3; var path = new CurveArray();
 path.Append(Line.CreateBound(new XYZ(-3,0,0), new XYZ(0,0,0)));
 path.Append(Arc.Create(new XYZ(0,0,0), new XYZ(R,0,R), new XYZ(R*Math.Sin(Math.PI/4), 0, R-R*Math.Cos(Math.PI/4))));
 path.Append(Line.CreateBound(new XYZ(R,0,R), new XYZ(R,0,R+3)));
 // oracle finding: NewSweep wants the profile drawn in the XY plane (z=0, coordinates relative to the path start); Revit maps it onto the plane perpendicular to the path start (profiles drawn in the true perpendicular plane raise ArgumentException)
 var pr = new CurveArray(); var p = new XYZ[] { new XYZ(-0.3,-0.3,0), new XYZ(0.3,-0.3,0), new XYZ(0.3,-0.1,0), new XYZ(-0.1,-0.1,0), new XYZ(-0.1,0.3,0), new XYZ(-0.3,0.3,0) };
 for (int i = 0; i < 6; i++) pr.Append(Line.CreateBound(p[i], p[(i+1)%6]));
 var sprof = app.Create.NewCurveLoopsProfile(one(pr)); fd.FamilyCreate.NewSweep(true, path, spx, sprof, 0, ProfilePlaneLocation.Start);''')
F['fam_sweep_spline_path']=famfeat("sweep of a circle r=0.25 along a HERMITE SPLINE path (S-curve in the XZ plane); variant: spline end point moved (+1 in x)",_HELP+r'''
 double dx = v==0 ? 0 : 1; var path = new CurveArray();
 var pts = new List<XYZ> { new XYZ(0,0,0), new XYZ(2,0,1.5), new XYZ(4+dx,0,1), new XYZ(6+dx,0,3) };
 path.Append(HermiteSpline.Create(pts, false));
 var spl = (Curve)path.get_Item(0); var t0 = spl.ComputeDerivatives(0, true).BasisX.Normalize(); out_ += "t0=" + t0.X + "," + t0.Y + "," + t0.Z + ";";
 var ca = circ(XYZ.Zero, 0.25);
 var sprof = app.Create.NewCurveLoopsProfile(one(ca)); fd.FamilyCreate.NewSweep(true, path, spx, sprof, 0, ProfilePlaneLocation.Start);''')
F['fam_sweep_3dpath']=famfeat("sweep of a 0.3x0.3 square along a true 3D path of three connected model lines (x, then y, then z direction); variant: last segment longer",_HELP+r'''
 double h = v==0 ? 3 : 5;
 var pp = new XYZ[] { new XYZ(0,0,0), new XYZ(4,0,0), new XYZ(4,3,0), new XYZ(4,3,h) };
 var refs = new ReferenceArray();
 for (int i = 0; i < 3; i++) { var ln = Line.CreateBound(pp[i], pp[i+1]); var dir = (pp[i+1]-pp[i]).Normalize(); var nrm = Math.Abs(dir.Z) > 0.9 ? XYZ.BasisX : XYZ.BasisZ; var plN = dir.CrossProduct(nrm).Normalize(); var spp = SketchPlane.Create(fd, Plane.CreateByNormalAndOrigin(plN, pp[i])); var mc = fd.FamilyCreate.NewModelCurve(ln, spp); refs.Append(mc.GeometryCurve.Reference); }
 var pl0 = Plane.CreateByNormalAndOrigin(XYZ.BasisX, pp[0]); var ca = new CurveArray(); var q = new XYZ[] { new XYZ(-0.15,-0.15,0), new XYZ(0.15,-0.15,0), new XYZ(0.15,0.15,0), new XYZ(-0.15,0.15,0) }; for (int i = 0; i < 4; i++) ca.Append(Line.CreateBound(q[i], q[(i+1)%4]));
 var sprof = app.Create.NewCurveLoopsProfile(one(ca)); fd.FamilyCreate.NewSweep(true, refs, sprof, 0, ProfilePlaneLocation.Start);''')
F['fam_blend_circle']=famfeat("blend of bottom circle r=1.5 at z=0 to top circle r=0.6 at z=4 centred x offset 1 (variant top r=0.9): cone-like loft with oblique axis",_HELP+r'''
 double rt = v==0 ? 0.6 : 0.9; var bot = circ(new XYZ(0,0,0), 1.5); var top = circ(new XYZ(1,0,4), rt);
 fd.FamilyCreate.NewBlend(true, top, bot, sp);''')
F['fam_blend_twist']=famfeat("blend of bottom square 2x2 at z=0 to a top square 2x2 ROTATED 45 degrees at z=4 (variant 30 degrees): twisted loft, ruled/bilinear faces",_HELP+r'''
 double a = (v==0 ? 45 : 30) * Math.PI / 180; var bot = rect(-1,-1,1,1,0); var top = new CurveArray();
 var q = new XYZ[4]; double[][] c = { new[]{-1.0,-1.0}, new[]{1.0,-1.0}, new[]{1.0,1.0}, new[]{-1.0,1.0} };
 for (int i = 0; i < 4; i++) q[i] = new XYZ(c[i][0]*Math.Cos(a)-c[i][1]*Math.Sin(a), c[i][0]*Math.Sin(a)+c[i][1]*Math.Cos(a), 4);
 for (int i = 0; i < 4; i++) top.Append(Line.CreateBound(q[i], q[(i+1)%4]));
 fd.FamilyCreate.NewBlend(true, top, bot, sp);''')
F['fam_blend_rect_circle']=famfeat("blend of bottom rectangle 3x2 at z=0 to top circle r=0.8 at z=3 (variant r=1.0): different edge counts (4 lines -> 2 arcs)",_HELP+r'''
 double rt = v==0 ? 0.8 : 1.0; var bot = rect(-1.5,-1,1.5,1,0); var top = circ(new XYZ(0,0,3), rt);
 try { fd.FamilyCreate.NewBlend(true, top, bot, sp); } catch (Exception ex) { out_ += "blend_rect_circle ERR " + ex.Message.Split('\n')[0] + ";"; throw; }''')
F['fam_sweptblend']=famfeat("swept blend along a quarter-circle path in the XZ plane (r=3): start profile square 0.6, end profile circle r=0.2 (variant r=4)",_HELP+r'''
 double R = v==0?3:4; var path = new CurveArray(); path.Append(Arc.Create(new XYZ(R,0,0), new XYZ(0,0,R), new XYZ(R*Math.Cos(Math.PI/4), 0, R*Math.Sin(Math.PI/4))));
 var sq = new CurveArray(); var q = new XYZ[] { new XYZ(-0.3,-0.3,0), new XYZ(0.3,-0.3,0), new XYZ(0.3,0.3,0), new XYZ(-0.3,0.3,0) }; for (int i = 0; i < 4; i++) sq.Append(Line.CreateBound(q[i], q[(i+1)%4]));
 var cc = circ(new XYZ(0,0,0), 0.2); 
 // end profile lies in the plane at the path end (z=R), perpendicular to the path tangent (+z... tangent at end is -x): profile in plane x=0 -> draw as circle in YZ plane
 var cc2 = circ(XYZ.Zero, 0.2);
 var pr1 = app.Create.NewCurveLoopsProfile(one(sq)); var pr2 = app.Create.NewCurveLoopsProfile(one(cc2));
 fd.FamilyCreate.NewSweptBlend(true, path.get_Item(0), spx, pr1, pr2);''')
F['fam_void_revolve']=famfeat("solid box 4x4x4 minus a VOID revolve (cone cavity: triangle r=1.5,h=4 about the Z axis); variant r=1.8",_HELP+r'''
 fd.FamilyCreate.NewExtrusion(true, one(rect(-2,-2,2,2,0)), sp, 4);
 double R = v==0?1.5:1.8; var prof = new CurveArray(); prof.Append(Line.CreateBound(new XYZ(0,0,0), new XYZ(R,0,0))); prof.Append(Line.CreateBound(new XYZ(R,0,0), new XYZ(0,0,4))); prof.Append(Line.CreateBound(new XYZ(0,0,4), new XYZ(0,0,0)));
 fd.FamilyCreate.NewRevolution(false, one(prof), spx, Line.CreateBound(new XYZ(0,0,0), new XYZ(0,0,1)), 0, 2*Math.PI);''')
F['fam_void_sweep']=famfeat("solid box 6x2x2 minus a VOID sweep (circle r=0.4 along an arc path through the box, XZ plane); variant r=0.6",_HELP+r'''
 fd.FamilyCreate.NewExtrusion(true, one(rect(-3,-1,3,1,0)), sp, 2);
 double r = v==0?0.4:0.6; var path = new CurveArray(); path.Append(Arc.Create(new XYZ(-2.5,0,1), new XYZ(2.5,0,1), new XYZ(0,0,2.5)));
 var ca = new CurveArray(); var pl = Plane.CreateByNormalAndOrigin(new XYZ(0.9,0,0.43).Normalize(), new XYZ(-2.5,0,1));
 var cs = circ(XYZ.Zero, r);
 var sprof = app.Create.NewCurveLoopsProfile(one(cs)); fd.FamilyCreate.NewSweep(false, path, spx, sprof, 0, ProfilePlaneLocation.Start);''')
F['fam_void_blend']=famfeat("solid box 4x4x4 minus a VOID blend (bottom square 1.5 to top circle r=0.4, z 0..4); variant top r=0.7",_HELP+r'''
 fd.FamilyCreate.NewExtrusion(true, one(rect(-2,-2,2,2,0)), sp, 4);
 double rt = v==0?0.4:0.7; fd.FamilyCreate.NewBlend(false, circ(new XYZ(0,0,4), rt), rect(-0.75,-0.75,0.75,0.75,0), sp);''')

F['dbg_sweep']=famfeat("debug sweep variants",_HELP+r'''
 Func<string, CurveArray, CurveArray, bool> tr = (nm, pth, prc) => { try { var sp_ = app.Create.NewCurveLoopsProfile(one(prc)); fd.FamilyCreate.NewSweep(true, pth, spx, sp_, 0, ProfilePlaneLocation.Start); out_ += nm + "=OK;"; return true; } catch (Exception e_) { out_ += nm + "=FAIL(" + e_.Message.Substring(0, 30) + ");"; return false; } };
 Func<double, double, double, CurveArray> rx = (x, y, z) => { var a_ = new CurveArray(); var q = new XYZ[] { new XYZ(x,y-0.2,z-0.2), new XYZ(x,y+0.2,z-0.2), new XYZ(x,y+0.2,z+0.2), new XYZ(x,y-0.2,z+0.2) }; for (int i = 0; i < 4; i++) a_.Append(Line.CreateBound(q[i], q[(i+1)%4])); return a_; };
 var p1 = new CurveArray(); p1.Append(Line.CreateBound(new XYZ(-3,0,0), new XYZ(0,0,0)));
 tr("line_rectYZ", p1, rx(-3,0,0));
 var p2 = new CurveArray(); p2.Append(Line.CreateBound(new XYZ(0,0,0), new XYZ(3,0,0)));
 tr("line2_rectYZ", p2, rx(0,0,0));
 var p3 = new CurveArray(); p3.Append(Line.CreateBound(new XYZ(-3,0,0), new XYZ(0,0,0))); p3.Append(Arc.Create(new XYZ(0,0,0), new XYZ(2,0,2), new XYZ(2*Math.Sin(Math.PI/4), 0, 2-2*Math.Cos(Math.PI/4))));
 tr("line_arc", p3, rx(-3,0,0));
 var p4 = new CurveArray(); p4.Append(HermiteSpline.Create(new List<XYZ> { new XYZ(0,0,0), new XYZ(2,0,1.5), new XYZ(4,0,1), new XYZ(6,0,3) }, false));
 var t0 = ((Curve)p4.get_Item(0)).ComputeDerivatives(0, true).BasisX.Normalize();
 tr("spline_rectYZ", p4, rx(0,0,0));
 var pl = Plane.CreateByNormalAndOrigin(t0, XYZ.Zero); var cc = new CurveArray(); cc.Append(Arc.Create(pl, 0.25, 0, Math.PI)); cc.Append(Arc.Create(pl, 0.25, Math.PI, 2*Math.PI));
 tr("spline_circ", p4, cc);
 var cc2 = new CurveArray(); cc2.Append(Arc.Create(new XYZ(0,0,0), 0.25, 0, Math.PI, XYZ.BasisY, XYZ.BasisZ)); cc2.Append(Arc.Create(new XYZ(0,0,0), 0.25, Math.PI, 2*Math.PI, XYZ.BasisY, XYZ.BasisZ));
 tr("line2_circ", p2, cc2);
 var pz = new CurveArray(); pz.Append(Line.CreateBound(new XYZ(0,0,0), new XYZ(0,0,3)));
 Func<double, CurveArray> rz = (z) => { var a_ = new CurveArray(); var q = new XYZ[] { new XYZ(-0.2,-0.2,z), new XYZ(0.2,-0.2,z), new XYZ(0.2,0.2,z), new XYZ(-0.2,0.2,z) }; for (int i = 0; i < 4; i++) a_.Append(Line.CreateBound(q[i], q[(i+1)%4])); return a_; };
 tr("linez_rectXY", pz, rz(0));
 var pz2 = new CurveArray(); pz2.Append(Line.CreateBound(new XYZ(2,0,0), new XYZ(2,0,3)));
 Func<double, CurveArray> rz2 = (z) => { var a_ = new CurveArray(); var q = new XYZ[] { new XYZ(1.8,-0.2,z), new XYZ(2.2,-0.2,z), new XYZ(2.2,0.2,z), new XYZ(1.8,0.2,z) }; for (int i = 0; i < 4; i++) a_.Append(Line.CreateBound(q[i], q[(i+1)%4])); return a_; };
 tr("linez_off_rectXY", pz2, rz2(0));
 var pa = new CurveArray(); pa.Append(Arc.Create(new XYZ(3,0,0), new XYZ(0,0,3), new XYZ(3*Math.Cos(Math.PI/4), 0, 3*Math.Sin(Math.PI/4))));
 tr("arc_vert_rectXY", pa, rz2(0));
 var pb = new CurveArray(); pb.Append(Line.CreateBound(new XYZ(0,0,0), new XYZ(0,0,3))); pb.Append(Line.CreateBound(new XYZ(0,0,3), new XYZ(2,0,3)));
 tr("two_lines", pb, rz(0));
 Func<double, double, double, CurveArray> rzc = (cx, cy, cz) => { var a_ = new CurveArray(); var q = new XYZ[] { new XYZ(cx-0.2,cy-0.2,cz), new XYZ(cx+0.2,cy-0.2,cz), new XYZ(cx+0.2,cy+0.2,cz), new XYZ(cx-0.2,cy+0.2,cz) }; for (int i = 0; i < 4; i++) a_.Append(Line.CreateBound(q[i], q[(i+1)%4])); return a_; };
 Func<double, double, double, CurveArray> ryc = (cx, cy, cz) => { var a_ = new CurveArray(); var q = new XYZ[] { new XYZ(cx-0.2,cy,cz-0.2), new XYZ(cx+0.2,cy,cz-0.2), new XYZ(cx+0.2,cy,cz+0.2), new XYZ(cx-0.2,cy,cz+0.2) }; for (int i = 0; i < 4; i++) a_.Append(Line.CreateBound(q[i], q[(i+1)%4])); return a_; };
 tr("xline_XYat0", p2, rzc(0,0,0));
 tr("xline_XYat0_pathstart3", p1, rzc(0,0,0));
 tr("xline_XYat_start", p1, rzc(-3,0,0));
 tr("xline_XZ", p2, ryc(0,0,0));
 tr("spline_XY", p4, rzc(0,0,0));
 var pz3 = new CurveArray(); pz3.Append(Line.CreateBound(new XYZ(1,2,3), new XYZ(1,2,6)));
 tr("zline_off123_XYat0", pz3, rzc(0,0,0));
 tr("zline_off123_XYatstart", pz3, rzc(1,2,3));
 tr("zline_off123_XYat1_2_0", pz3, rzc(1,2,0));''')

F['view_dims_fit']=_vf("(dims) 9 linear dimensions between the interior faces of the two vertical walls (x=0, x=20) at y = 1,2.5,4,5.5,7,8.5,10,12,13.5 and 6 between the interior faces of the two horizontal walls (y=0, y=14) at x = 2,5,8,11,14,17; all in the VR plan (level VR1 z=20)","""
 Func<bool, List<Wall>> wl = (vert) => new FilteredElementCollector(d).OfClass(typeof(Wall)).Cast<Wall>().Where(x => x.LevelId == vl.Id).Where(x => { var c = (x.Location as LocationCurve).Curve; return vert ? Math.Abs(c.GetEndPoint(0).X - c.GetEndPoint(1).X) < 0.01 : Math.Abs(c.GetEndPoint(0).Y - c.GetEndPoint(1).Y) < 0.01; }).OrderBy(x => { var c = (x.Location as LocationCurve).Curve; return vert ? c.GetEndPoint(0).X : c.GetEndPoint(0).Y; }).ToList();
 var vw = wl(true); var hw = wl(false); out_ += "vwalls=" + vw.Count + " hwalls=" + hw.Count + ";";
 foreach (double y in new double[] { 1, 2.5, 4, 5.5, 7, 8.5, 10, 12, 13.5 }) { try { var ra = new ReferenceArray(); ra.Append(HostObjectUtils.GetSideFaces(vw.First(), ShellLayerType.Interior)[0]); ra.Append(HostObjectUtils.GetSideFaces(vw.Last(), ShellLayerType.Interior)[0]); d.Create.NewDimension(vp, Line.CreateBound(new XYZ(0, y, 20), new XYZ(20, y, 20)), ra); out_ += "dimV" + y + " ok;"; } catch (Exception ex) { out_ += "dimV" + y + "ERR " + ex.Message.Split((char)10)[0] + ";"; } }
 foreach (double x in new double[] { 2, 5, 8, 11, 14, 17 }) { try { var ra = new ReferenceArray(); ra.Append(HostObjectUtils.GetSideFaces(hw.First(), ShellLayerType.Interior)[0]); ra.Append(HostObjectUtils.GetSideFaces(hw.Last(), ShellLayerType.Interior)[0]); d.Create.NewDimension(vp, Line.CreateBound(new XYZ(x, 0, 20), new XYZ(x, 14, 20)), ra); out_ += "dimH" + x + " ok;"; } catch (Exception ex) { out_ += "dimH" + x + "ERR " + ex.Message.Split((char)10)[0] + ";"; } }
""")

F['view_tags_fit']=_vf("(NOT USABLE AS IS: the seeds have no tag family loaded, IndependentTag.Create fails with 'no loaded tag type'; load a tag family first, see tools/finish_all.py) (tags) in the VR plan: 6 wall tags on the south wall (Mark A) with heads at x=2,5,8,11,14,17 y=-2 (no leader), one wall tag per other wall (heads: east (23,7), north (10,16), west (-3,7)), the door tag (head (6,3)) and the window tag (head (17,7)), one wall tag with leader (head (10,-4)); each in its own try","""
 var walls = new FilteredElementCollector(d).OfClass(typeof(Wall)).Cast<Wall>().Where(x => x.LevelId == vl.Id).OrderBy(x => { var c = (x.Location as LocationCurve).Curve; return c.GetEndPoint(0).X * 1000 + c.GetEndPoint(0).Y; }).ToList();
 var south = walls.First(x => Math.Abs((x.Location as LocationCurve).Curve.GetEndPoint(0).Y) < 0.01 && Math.Abs((x.Location as LocationCurve).Curve.GetEndPoint(1).Y) < 0.01);
 var east = walls.First(x => Math.Abs((x.Location as LocationCurve).Curve.GetEndPoint(0).X - 20) < 0.01 && Math.Abs((x.Location as LocationCurve).Curve.GetEndPoint(1).X - 20) < 0.01);
 var north = walls.First(x => Math.Abs((x.Location as LocationCurve).Curve.GetEndPoint(0).Y - 14) < 0.01 && Math.Abs((x.Location as LocationCurve).Curve.GetEndPoint(1).Y - 14) < 0.01);
 var west = walls.First(x => Math.Abs((x.Location as LocationCurve).Curve.GetEndPoint(0).X) < 0.01 && Math.Abs((x.Location as LocationCurve).Curve.GetEndPoint(1).X) < 0.01);
 var win = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).OfCategory(BuiltInCategory.OST_Windows).First();
 Action<string, Element, double, double, bool> tg = (nm, el, x, y, ld) => { try { var tgx = IndependentTag.Create(d, vp.Id, new Reference(el), ld, TagMode.TM_ADDBY_CATEGORY, TagOrientation.Horizontal, new XYZ(x, y, 20)); out_ += nm + " ok " + tgx.Id + ";"; } catch (Exception ex) { out_ += nm + "ERR " + ex.Message.Split((char)10)[0] + ";"; } };
 foreach (double x in new double[] { 2, 5, 8, 11, 14, 17 }) tg("tS" + x, south, x, -2, false);
 tg("tE", east, 23, 7, false); tg("tN", north, 10, 16, false); tg("tW", west, -3, 7, false); tg("tDoor", door0, 6, 3, false); tg("tWin", win, 17, 7, false); tg("tLead", south, 10, -4, true);
""")

F['view_regions_fit']=_vf("(regions) 8 rectangular filled regions in the VR plan (level VR1 z=20), (x,y,w,d) = (14,9,3,2) (2,2,4,3) (8,2,2,6) (3,8,6,2) (15,2,2.5,2.5) (10,10,5,3) (1,5,1,1) (6,6,7,2): each its own FilledRegion with 4 line boundary curves","""
 var frt = new FilteredElementCollector(d).OfClass(typeof(FilledRegionType)).FirstElement().Id;
 foreach (var r in new double[][] { new double[] {14,9,3,2}, new double[] {2,2,4,3}, new double[] {8,2,2,6}, new double[] {3,8,6,2}, new double[] {15,2,2.5,2.5}, new double[] {10,10,5,3}, new double[] {1,5,1,1}, new double[] {6,6,7,2} }) {
  try { var lp = new CurveLoop(); var q = new XYZ[] { new XYZ(r[0], r[1], 20), new XYZ(r[0] + r[2], r[1], 20), new XYZ(r[0] + r[2], r[1] + r[3], 20), new XYZ(r[0], r[1] + r[3], 20) }; for (int i = 0; i < 4; i++) lp.Append(Line.CreateBound(q[i], q[(i + 1) % 4])); FilledRegion.Create(d, frt, vp.Id, new List<CurveLoop> { lp }); out_ += "region ok;"; } catch (Exception ex) { out_ += "regionERR " + ex.Message.Split((char)10)[0] + ";"; } }
""")

F['view_tags_types']=_vf("(tag types) copy the Wall, Door and Window tag FamilySymbols from the default project template (Default_M_ENU.rte) into the file with CopyElements (what tools/finish_all.py does); no tags placed",r"""
 foreach (var stem in new string[] { "Wall", "Door", "Window" }) {
  try { var tp = @"C:\\ProgramData\\Autodesk\\RVT " + d.Application.VersionNumber + @"\\Templates\\Default_M_ENU.rte"; var src = d.Application.OpenDocumentFile(tp);
   var sc = src.Settings.Categories.Cast<Category>().FirstOrDefault(c => c.Name == stem + " Tags"); var sym = sc == null ? null : new FilteredElementCollector(src).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().FirstOrDefault(f => f.Category != null && f.Category.Id.Equals(sc.Id));
   if (sym != null) { var cp = ElementTransformUtils.CopyElements(src, new List<ElementId> { sym.Id }, d, Transform.Identity, new CopyPasteOptions()); out_ += stem + " copied " + cp.Count + " (" + sym.Name + ");"; } else out_ += stem + " nosym;"; src.Close(false); }
  catch (Exception ex) { out_ += stem + "ERR " + ex.Message.Split((char)10)[0] + ";"; } }
""")

# ---------------- more SHIFT rosettas (2026-10-17, c3-writer): beams, wall + foundation, MEP duct/pipe, group; variant translated (+100,+50,0) ----------------
F['beam_shift']=("[SEED house_base] two structural framing beams (first symbol UB305x165x40) on Level 1: (60,70,10)-(80,70,10) and (60,70,10)-(60,90,10); variant translated (+100,+50)",r'''
double DX = v == 1 ? 100 : 0, DY = v == 1 ? 50 : 0;
using (var t = new Transaction(d, "beam")) { t.Start();
 var sym = new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsElementType().Cast<FamilySymbol>().First(); if (!sym.IsActive) sym.Activate(); d.Regenerate();
 var b1 = d.Create.NewFamilyInstance(Line.CreateBound(new XYZ(60+DX,70+DY,10), new XYZ(80+DX,70+DY,10)), sym, l1, Autodesk.Revit.DB.Structure.StructuralType.Beam);
 var b2 = d.Create.NewFamilyInstance(Line.CreateBound(new XYZ(60+DX,70+DY,10), new XYZ(60+DX,90+DY,10)), sym, l1, Autodesk.Revit.DB.Structure.StructuralType.Beam);
 t.Commit(); out_ += "beams=" + b1.Id + "," + b2.Id; }
''')
F['wallfound_shift']=("[SEED house_base] wall (first basic WallType) (60,100)-(80,100) height 9 on Level 1 with a continuous WallFoundation (first WallFoundationType); variant translated (+100,+50)",r'''
double DX = v == 1 ? 100 : 0, DY = v == 1 ? 50 : 0;
using (var t = new Transaction(d, "wf")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var w = Wall.Create(d, Line.CreateBound(new XYZ(60+DX,100+DY,0), new XYZ(80+DX,100+DY,0)), wt.Id, l1.Id, 9, 0, false, false); d.Regenerate();
 var ft = new FilteredElementCollector(d).OfClass(typeof(WallFoundationType)).First();
 var f = WallFoundation.Create(d, ft.Id, w.Id); t.Commit(); out_ += "wall=" + w.Id + " found=" + f.Id; }
''')
F['duct_shift']=("[SEED house_base] one straight Duct (first MechanicalSystemType, first DuctType) (60,110,9)-(80,110,9) on Level 1 plus one straight Pipe (first PipingSystemType/PipeType) (60,114,8)-(80,114,8); variant translated (+100,+50)",r'''
double DX = v == 1 ? 100 : 0, DY = v == 1 ? 50 : 0;
using (var t = new Transaction(d, "mep")) { t.Start();
 var ms = new FilteredElementCollector(d).OfClass(typeof(Autodesk.Revit.DB.Mechanical.MechanicalSystemType)).First(); var dt = new FilteredElementCollector(d).OfClass(typeof(Autodesk.Revit.DB.Mechanical.DuctType)).First();
 var du = Autodesk.Revit.DB.Mechanical.Duct.Create(d, ms.Id, dt.Id, l1.Id, new XYZ(60+DX,110+DY,9), new XYZ(80+DX,110+DY,9));
 var ps = new FilteredElementCollector(d).OfClass(typeof(Autodesk.Revit.DB.Plumbing.PipingSystemType)).First(); var pt = new FilteredElementCollector(d).OfClass(typeof(Autodesk.Revit.DB.Plumbing.PipeType)).First();
 var pi = Autodesk.Revit.DB.Plumbing.Pipe.Create(d, ps.Id, pt.Id, l1.Id, new XYZ(60+DX,114+DY,8), new XYZ(80+DX,114+DY,8));
 t.Commit(); out_ += "duct=" + du.Id + " pipe=" + pi.Id; }
''')
F['group_shift']=("[SEED house_base] two walls (60,120)-(70,120) and (70,120)-(70,130) height 9 on Level 1 made into a model Group; variant translated (+100,+50)",r'''
double DX = v == 1 ? 100 : 0, DY = v == 1 ? 50 : 0;
using (var t = new Transaction(d, "grp")) { t.Start();
 var wt = new FilteredElementCollector(d).OfClass(typeof(WallType)).Cast<WallType>().First(x => x.Kind == WallKind.Basic);
 var w1 = Wall.Create(d, Line.CreateBound(new XYZ(60+DX,120+DY,0), new XYZ(70+DX,120+DY,0)), wt.Id, l1.Id, 9, 0, false, false);
 var w2 = Wall.Create(d, Line.CreateBound(new XYZ(70+DX,120+DY,0), new XYZ(70+DX,130+DY,0)), wt.Id, l1.Id, 9, 0, false, false); d.Regenerate();
 var g = d.Create.NewGroup(new List<ElementId> { w1.Id, w2.Id }); t.Commit(); out_ += "group=" + g.Id; }
''')
