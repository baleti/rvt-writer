known=[(137,4,73),(141,4,75),(155,5,65),(179,5,65),(195,5,65),(204,5,65),(366,6,65),(415,6,65),(496,6,65),(528,6,67),(560,6,71),(634,7,65),(667,7,65),(1350,7,85),(4408,9,69),(12960,11,65),(13065,11,65),(17144,11,67),(17656,11,69),(19703,11,77),(20215,11,79),(65249,11,255)]
def rule(N,umin=65,dmax=11):
    B=8*N; best=None
    for u in range(umin,B//2+1):
        if B%u>7: continue
        L=B//u
        d=1
        while (1<<d)-1<L: d+=1
        if d>dmax: continue
        cost=d*u
        if best is None or cost<best[0]: best=(cost,d,u)
    return best[1:] if best else None
if __name__=='__main__':
    for N,d,u in known:
        r=rule(N); print(N,(d,u),r,'OK' if r==(d,u) else 'XX')
