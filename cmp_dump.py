import sys
SUB=[]
def load(f,sub=False):
    d={}
    for l in open(f,encoding='utf-8'):
        if sub:
            for o,n in SUB: l=l.replace(o,n)
        p=l.rstrip('\n').split('|')
        if p[2] in ('PropertySetElement',): p=p[:6]
        p=[x for x in p if not x.startswith('File Path=')]
        if p[1:2]==['Element'] or True: p=[x for x in p if not x.startswith(('Reuse ','Copy windows','Add prefix','Add suffix'))]
        d[(p[1])]=p
    return d
import os
SUB[:]=[tuple(x.split('=>')) for x in os.environ.get('SUB','').split(';') if x]
a=load(sys.argv[1]); b=load(sys.argv[2],True)
only_a=[k for k in a if k not in b]; only_b=[k for k in b if k not in a]
diff=[k for k in a if k in b and a[k]!=b[k]]
print('elements',len(a),len(b),'onlyA',len(only_a),'onlyB',len(only_b),'changed',len(diff))
for k in diff[:int(sys.argv[3]) if len(sys.argv)>3 else 8]:
    x,y=a[k],b[k]
    sx,sy=set(x),set(y)
    print(' ',k,x[2],x[4][:40],'A-B:',[s[:80] for s in sx-sy][:4],'B-A:',[s[:80] for s in sy-sx][:4])
for k in only_a[:5]: print(' onlyA',a[k][:6])
for k in only_b[:5]: print(' onlyB',b[k][:6])
