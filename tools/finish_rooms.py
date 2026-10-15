#!/usr/bin/env python3
"""finish_rooms.py YEAR IN OUT MANIFEST : Revit finishing pass (flagged: rooms are created by the Revit API, everything else is writer output).
For each manifest['room_requests'] = [level_id, x, y, name, number] create a Room at that point; SaveAs OUT."""
import sys,os,json; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign')
import guest
year=int(sys.argv[1]); fin=os.path.abspath(sys.argv[2]); fout=os.path.abspath(sys.argv[3]); man=json.load(open(sys.argv[4]))
req=man.get('room_requests',[])
lines=''.join('  rooms.Add(new object[] { %d, %r, %r, @"%s", @"%s" });\n'%(r[0],float(r[1]),float(r[2]),r[3],r[4]) for r in req).replace("'","")
CS=r'''
using Autodesk.Revit.DB; using Autodesk.Revit.DB.Architecture; using System.Linq; using System.Collections.Generic;
var app = UIApp.Application; var d = app.OpenDocumentFile(@"C:\wl\fr_in.rte");
var rooms = new List<object[]>();
__LINES__
int ok = 0;
using (var t = new Transaction(d, "rooms")) { t.Start();
 foreach (var r in rooms) { try { var lv = d.GetElement(new ElementId((int)r[0])) as Level; var nr = d.Create.NewRoom(lv, new UV((double)r[1], (double)r[2])); nr.Name = (string)r[3]; nr.Number = (string)r[4]; Console.WriteLine("FRROOM " + nr.Number + " area=" + nr.Area); if (nr.Area > 0) ok++; } catch (Exception ex) { Console.WriteLine("FRERR " + ex.Message.Split((char)10)[0]); } }
 t.Commit(); }
d.SaveAs(@"C:\wl\out\fr_out.rte", new SaveAsOptions { OverwriteExistingFile = true }); d.Close(false);
Console.WriteLine("FINISHED rooms=" + rooms.Count + " enclosed=" + ok);
'''.replace('__LINES__',lines)
with guest.vmlock():
    guest.put(fin,'C:/wl/fr_in.rte'); p=guest.fresh(year)
    o=guest.run_job(year,p,CS,'fr',600); print(o[-1500:])
    if 'FINISHED' in o: guest.get('C:/wl/out/fr_out.rte',fout)
    guest.down(year)
