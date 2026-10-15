import pickle,sys,time
sys.path.insert(0,'/home/user1/rvt-research/write-lab')
from gf2 import *
T=pickle.load(open('/tmp/claude-1000/trailers.pkl','rb'))
full=[t for t in T if t[3][0]==0][:6]
def bits_lsb(b):  # list->int, first bit (LSB of first byte) = highest degree
    return int(''.join(format(x,'08b')[::-1] for x in b),2)
def bits_msb(b): return int.from_bytes(b,'big')
def mk(payload,trailer,order,mode):
    f=bits_lsb if order=='lsb' else bits_msb
    P=f(payload); 
    ts=''.join(format(x,'08b')[::-1] if order=='lsb' else format(x,'08b') for x in trailer)
    if mode=='parity2805': tb=ts[12:2817]
    elif mode=='withzero': tb=ts[:2817]
    elif mode=='full': tb=ts
    return (P<<len(tb)) | int(tb,2)
for order in ('lsb','msb'):
    for mode in ('parity2805','withzero','full'):
        a=mk(full[0][4],full[0][3],order,mode); b=mk(full[1][4],full[1][3],order,mode)
        t0=time.time(); g=pgcd(a,b)
        print(order,mode,'gcd deg',deg(g),'%.1fs'%(time.time()-t0),flush=True)
        # also reversed polynomial convention
        ra=int(bin(a)[2:].zfill(0)[::-1],2); rb=int(bin(b)[2:][::-1],2)
        g2=pgcd(ra,rb); print('   reversed deg',deg(g2),flush=True)
