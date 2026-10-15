import sys; sys.path.insert(0,'campaign')
import guest
y=int(sys.argv[1])
with guest.vmlock():
    r=guest.h2("%s/gssh powershell -NoProfile -ExecutionPolicy Bypass -File C:/ci/revit-up.ps1 -Year %d -TimeoutSec 150"%(guest.RD,y),260); print(r.stdout[-600:],r.stderr[-300:])
    print(guest.script(r'''Get-Process Revit -ErrorAction SilentlyContinue | Select Id,Path,MainWindowTitle | Format-List | Out-String
Get-ChildItem "C:\Users\*\AppData\Roaming\Autodesk\Revit\Addins\%d" -ErrorAction SilentlyContinue | Select -Expand FullName
Get-ChildItem "C:\ProgramData\Autodesk\Revit\Addins\%d" | Select -Expand Name
Get-Content "$env:APPDATA\revit-ballet\logs\*.log" -Tail 15 -ErrorAction SilentlyContinue''' % (y,y),120))
    print(guest.journal_tail(y,25))
    guest.down(y)
