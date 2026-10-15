import sys; sys.path.insert(0,'campaign')
import guest
with guest.vmlock():
    for y in (2020,2024,2026,2021,2022,2023,2025):
        try: guest.h2("%s/gssh powershell -NoProfile -ExecutionPolicy Bypass -File C:/ci/revit-down.ps1 -Year %d"%(guest.RD,y),60)
        except Exception as e: pass
    r=guest.h2("%s/gssh powershell -NoProfile -ExecutionPolicy Bypass -File C:/ci/trust-and-sign.ps1 -Years 2020,2021,2022,2023,2024,2025,2026"%guest.RD,300); print(r.stdout[-800:],flush=True)
    p=guest.fresh(2024); print('2024 port',p,flush=True); guest.down(2024)
