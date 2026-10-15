import sys; sys.path.insert(0,'campaign')
import guest
for y in (2021,2022,2023,2025):
    with guest.vmlock():
        p=guest.fresh(y); print(y,'port',p,flush=True)
        if p: print(guest.run_job(y,p,'Console.WriteLine("HELLO "+UIApp.Application.VersionNumber);','yt%d'%y,200)[-200:],flush=True)
        guest.down(y)
