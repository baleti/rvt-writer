import sys,json
man=json.load(open(sys.argv[1])); geo={}
for l in open(sys.argv[2]):
    p=l.split()
    if len(p)>=8 and p[1] in('ModelLine','ModelCurve','CurveElement'): geo[int(p[0])]=tuple(map(float,p[2:8]))
bad=0
for nid,p0,p1 in man:
    g=geo.get(nid)
    if not g: bad+=1; print('missing',nid); continue
    if max(abs(g[0]-p0[0]),abs(g[1]-p0[1]),abs(g[3]-p1[0]),abs(g[4]-p1[1]))>1e-6: bad+=1; print('mismatch',nid,g,p0,p1)
print('segments',len(man),'in revit',len([k for k in geo if k>=man[0][0]]),'bad',bad)
# closure: consecutive end==start
cl=sum(1 for a,b in zip(man,man[1:]) if abs(a[2][0]-b[1][0])<1e-9 and abs(a[2][1]-b[1][1])<1e-9); print('chained joints',cl,'of',len(man)-1)
