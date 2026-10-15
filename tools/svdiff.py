import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,wledit
R=os.path.expanduser('~/rvt-research/rosetta/')
fa,fb=sys.argv[1],sys.argv[2]
ga=rvtgen.Gen(R+fa); gb=rvtgen.Gen(R+fb)
ia=set(ga.e.m.ids); ib=set(gb.e.m.ids)
new=sorted(ib-ia); print('new in B:',[(i,gb.e.trace(i)[2]['class']) for i in new]); print('gone in B:',sorted(ia-ib)[:10])
ch=[]
for i in sorted(ia&ib):
    try: ta=ga.template(i); tb=gb.template(i)
    except Exception as e: continue
    d=[k for k in ('rec','item','hdr') if ta[k]!=tb[k]]
    if d: ch.append((i,ta['cls'],d,len(ta['rec']),len(tb['rec'])))
print('changed shared records:',len(ch)); [print(' ',c) for c in ch[:40]]
