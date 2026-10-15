"""Revit stream page ECC (reverse engineered 2026-10-11, see LOG.md).
A page of N bytes (B=8N bits, bits taken LSB-first within each byte, in stream order) is u interleaved codewords:
bit j belongs to codeword j mod u, row j div u. Each codeword has L=B//u rows (B mod u trailing pad bits < 8 are zero);
the first L-d rows are data, the last d rows are the parity of a CRC with a primitive polynomial h(y) of degree d (MSB-first, zero init):
parity = (D(y) * y^d) mod h(y). (u,d) is a function of N only: minimise d*u over u>=65 with B mod u <= 7, d the smallest allowed degree with 2^d-1 >= L."""
import numpy as np
from functools import lru_cache
POLY={3:0b1011,4:0b10011,5:0b100101,6:0b1000011,7:0b10000011,9:0b1000010001,10:0b10000001001,11:0b100000000101}
ALLOWED=(3,4,5,6,7,9,11)   # 3 unverified; no 8 (no primitive trinomial) and no 10 (observed: N=6679 uses 11 though 10 would do)
@lru_cache(maxsize=None)
def params(N, umin=65, allowed=ALLOWED):
    B=8*N; best=None; dmax=max(allowed)
    for u in range(umin,min(B//2,255)+1):    # u <= 255 (never seen larger; N with no valid (u,d) do not exist)
        if B%u>7: continue
        L=B//u
        d=next((x for x in sorted(allowed) if (1<<x)-1>=L),None)
        if d is None: continue
        if best is None or d*u<best[0]: best=(d*u,d,u,L)
    return best[1:] if best else None
def data_capacity(N):
    d,u,L=params(N); return (u*(L-d))//8
def _bits(b,n):
    a=np.unpackbits(np.frombuffer(b,dtype=np.uint8),bitorder='little')
    return a
def _encode_bits(bits,N):
    """bits: uint8 array of length>=u*(L-d) (data bits, rest ignored). returns full page bits (length 8N)"""
    d,u,L=params(N); B=8*N
    full=np.zeros(B,dtype=np.uint8)
    nd=u*(L-d); n=min(len(bits),nd); full[:n]=bits[:n]
    grid=full[:u*L].reshape(L,u)
    mask=(1<<d)-1; taps=POLY[d]&mask
    st=np.zeros(u,dtype=np.int64)
    for t in range(L-d):
        fb=((st>>(d-1))&1)^grid[t]
        st=((st<<1)&mask)^(fb*taps)
    for tp in range(d):
        grid[L-d+tp]=(st>>(d-1-tp))&1
    full[:u*L]=grid.reshape(-1)
    return full
def parity(data,N):
    """full N-byte page: data (zero padded; spare bits zero) + parity + pad"""
    d,u,L=params(N); cap=(u*(L-d))//8
    assert len(data)<=cap,(len(data),cap)
    bits=np.unpackbits(np.frombuffer(bytes(data),dtype=np.uint8),bitorder='little')
    return np.packbits(_encode_bits(bits,N),bitorder='little').tobytes()
def check(page):
    """True if the page (N bytes) has a correct parity (spare data bits taken from the page itself)"""
    N=len(page); d,u,L=params(N)
    bits=np.unpackbits(np.frombuffer(bytes(page),dtype=np.uint8),bitorder='little')
    return np.array_equal(_encode_bits(bits,N)[:u*L],bits[:u*L]) and not bits[u*L:].any()
