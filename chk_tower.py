import sys,json
man=json.load(open(sys.argv[1])); lines={}; levels={}
for l in open(sys.argv[2]):
    p=l.split()
    if len(p)>=8 and p[1] in('ModelLine','ModelCurve'): lines[int(p[0])]=tuple(map(float,p[2:8]))
    if len(p)>=4 and p[1]=='Level': levels[int(p[0])]=(' '.join(p[2:-1]),float(p[-1]))
bl=[(i,n,z) for i,n,z in man['levels'] if i not in levels or levels[i][0]!=n or abs(levels[i][1]-z)>1e-9]
bn=0
for nid,sp,p0,p1,z in man['lines']:
    g=lines.get(nid)
    if not g or max(abs(g[0]-p0[0]),abs(g[1]-p0[1]),abs(g[3]-p1[0]),abs(g[4]-p1[1]),abs(g[2]-z),abs(g[5]-z))>1e-6: bn+=1
print('levels gen',len(man['levels']),'bad',len(bl),'| lines gen',len(man['lines']),'bad',bn)
# closure per level polygon
import collections
by=collections.defaultdict(list)
for nid,sp,p0,p1,z in man['lines']: by[sp].append((nid))
ok=0
for sp,ids in by.items():
    seg=[lines[i] for i in ids if i in lines]
    cl=all(abs(seg[i][3]-seg[(i+1)%len(seg)][0])<1e-6 and abs(seg[i][4]-seg[(i+1)%len(seg)][1])<1e-6 for i in range(len(seg)))
    ok+=cl
print('closed polygons',ok,'of',len(by))
