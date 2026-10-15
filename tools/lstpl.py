import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab/campaign'))
import guest
with guest.vmlock():
    print(guest.script(r'''Get-ChildItem "C:\ProgramData\Autodesk\RVT 2024\Templates" -Recurse -Filter *.rte | Select -Expand FullName''',120)[:3000])
