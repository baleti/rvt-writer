def deg(a): return a.bit_length()-1
def pmod(a,b):
    db=deg(b)
    while a.bit_length()>db:
        a^=b<<(a.bit_length()-1-db)
    return a
def pgcd(a,b):
    while b:
        a,b=b,pmod(a,b)
    return a
def pmul(a,b):
    r=0
    while b:
        if b&1: r^=a
        a<<=1; b>>=1
    return r
def sqr(a):
    # square polynomial over GF(2): spread bits
    r=0; i=0
    s=bin(a)[2:][::-1]
    return int(''.join(c+'0' for c in s[::-1]) if False else ('0'.join(bin(a)[2:])),2)
def mulmod(a,b,g):
    # a*b mod g, a,b < x^deg g ; schoolbook with shifting
    dg=deg(g); r=0
    while b:
        if b&1: r^=a
        b>>=1; a<<=1
        if a.bit_length()>dg: a^=g
    return r
