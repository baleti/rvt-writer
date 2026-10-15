import sys,os,hashlib; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import cfb,adiff
R=os.path.expanduser('~/rvt-research/rosetta/')
a,b=R+sys.argv[1],R+sys.argv[2]
ca=cfb.CFB(open(a,'rb').read()).streams(); cb=cfb.CFB(open(b,'rb').read()).streams()
for n in ca:
    try: x=adiff.graw(a,n); y=adiff.graw(b,n)
    except Exception as e: print(n,'ERR',str(e)[:40]); continue
    if x!=y:
        d=[i for i in range(min(len(x),len(y))) if x[i]!=y[i]]
        print(n,len(x),len(y),'differ bytes',len(d),'first',d[:6],'last',d[-3:],flush=True)
