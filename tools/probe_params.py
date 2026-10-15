import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); fin=os.path.abspath(sys.argv[2]); eid=sys.argv[3]
CS=r'''
using Autodesk.Revit.DB; using System.Linq; using System.Collections.Generic;
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\wl\pp_in.rte");
var e = d.GetElement(new ElementId(__ID__));
foreach (Parameter p in e.Parameters) { if (p.Definition.Name.StartsWith("Ros")) { string o = "PP " + p.Definition.Name + " shared=" + p.IsShared + " type=" + p.StorageType; try { o += " has=" + p.HasValue; } catch (Exception ex) { o += " HASERR"; } try { o += " int=" + (p.StorageType == StorageType.Integer ? p.AsInteger().ToString() : "") + " dbl=" + (p.StorageType == StorageType.Double ? p.AsDouble().ToString() : "") + " str=" + (p.StorageType == StorageType.String ? p.AsString() : ""); } catch (Exception ex) { o += " VALERR " + ex.Message.Split((char)10)[0]; } Console.WriteLine(o); } }
Console.WriteLine("PP total params " + e.Parameters.Size);
var pes = new FilteredElementCollector(d).OfClass(typeof(ParameterElement)).Cast<ParameterElement>().Where(x => x.Name.StartsWith("Ros")).ToList();
foreach (var pe in pes) { Console.WriteLine("PE " + pe.Id + " " + pe.Name + " " + pe.GetType().Name + " " + pe.GetDefinition().GetDataType().TypeId); }
var bm = d.ParameterBindings.ForwardIterator(); int nb = 0; while (bm.MoveNext()) { if (bm.Key.Name.StartsWith("Ros")) { var b = bm.Current as ElementBinding; Console.WriteLine("BIND " + bm.Key.Name + " " + (b != null ? string.Join(",", b.Categories.Cast<Category>().Select(c => c.Name)) : "null")); nb++; } }
d.Close(false);
'''.replace('__ID__',eid)
with guest.vmlock():
    guest.put(fin,'C:/wl/pp_in.rte'); p=guest.fresh(year)
    print(guest.run_job(year,p,CS,'pp',600)[-2500:]); guest.down(year)
