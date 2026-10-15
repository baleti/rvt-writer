import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen
f,tid=sys.argv[1],int(sys.argv[2]); g=rvtgen.Gen(f); t=g.template(tid)
print(t['cls'],len(t['rec']),len(t['hdr']),len(t['item']))
for l in t['log']: print(l)
