import sys; sys.path.insert(0,'campaign')
import guest
with guest.vmlock():
    for s in ("install.ps1 -Years 2021,2022,2023,2025","trust-and-sign.ps1 -Years 2021,2022,2023,2025","revit-ini.ps1 -Years 2021,2022,2023,2025 -NoGpu"):
        r=guest.h2("%s/gssh powershell -NoProfile -ExecutionPolicy Bypass -File C:/ci/%s"%(guest.RD,s),600)
        print(s,r.returncode,(r.stdout+r.stderr)[-500:],flush=True)
