"""rvtw: paged / gzip-member / ECC stream writer for Revit files (see LOG.md)"""
import sys, zlib, struct
sys.path.insert(0,'/home/user1/rvt-research'); sys.path.insert(0,'/home/user1/rvt-research/write-lab')
import numpy as np
import cfb, ecc
PAGE_STORED=65249; PAGE_PAYLOAD=64896
GZ=b'\x1f\x8b\x08\x00'
PLAIN={'BasicFileInfo','Contents','TransmissionData','ProjectInformation','RevitPreview4.0'}

class Stream:
    """An ECC-paged stream: payload bytes (data of all pages) + layout of the last page."""
    def __init__(self, data):
        self.orig=data
        full=len(data)//PAGE_STORED; self.full=full
        last=data[full*PAGE_STORED:]
        self.N_last=len(last)
        parts=[data[i*PAGE_STORED:i*PAGE_STORED+PAGE_PAYLOAD] for i in range(full)]
        if last:
            d,u,L=ecc.params(len(last)); cap=(u*(L-d))//8
            parts.append(last[:cap]); self.cap_last=cap
            bits=np.unpackbits(np.frombuffer(last,dtype=np.uint8),bitorder='little')
            self.spare=bits[cap*8:u*(L-d)].copy()
        else: self.cap_last=0; self.spare=np.zeros(0,dtype=np.uint8)
        self.payload=b''.join(parts)
    def build(self, payload=None, N_last=None, keep_spare=False):
        payload=self.payload if payload is None else payload
        full=len(payload)//PAGE_PAYLOAD; rem=len(payload)-full*PAGE_PAYLOAD
        out=[]
        for i in range(full):
            out.append(ecc.parity(payload[i*PAGE_PAYLOAD:(i+1)*PAGE_PAYLOAD],PAGE_STORED))
        tail=payload[full*PAGE_PAYLOAD:]
        if N_last is None:
            N_last=self.N_last if (full==self.full) else None
        if tail or N_last:
            if N_last is None or ecc.data_capacity(N_last)<len(tail):
                N_last=min_last_page(len(tail))
            if keep_spare and len(self.spare):
                d,u,L=ecc.params(N_last); nd=u*(L-d)
                bits=np.zeros(nd,dtype=np.uint8); tb=np.unpackbits(np.frombuffer(tail,dtype=np.uint8),bitorder='little'); bits[:len(tb)]=tb
                sp=self.spare[:nd-len(tb)] if True else None
                if len(sp)==nd-len(tb): bits[len(tb):]=sp
                out.append(np.packbits(ecc._encode_bits(bits,N_last),bitorder='little').tobytes())
            else:
                out.append(ecc.parity(tail,N_last))
        return b''.join(out)

def min_last_page(r):
    """smallest N whose data capacity >= r bytes"""
    N=max(r+8,137)
    while True:
        p=ecc.params(N)
        if p and ecc.data_capacity(N)>=r: return N
        N+=1

def members(payload, start):
    """list of (pos, end) gzip members (end includes the 8-byte crc/isize); skipping 32-byte frames between them"""
    out=[]; pos=start
    while pos+10<=len(payload) and payload[pos:pos+4]==GZ:
        do=zlib.decompressobj(-15)
        try: raw=do.decompress(payload[pos+10:])
        except zlib.error: break
        if not do.eof: break
        end=len(payload)-len(do.unused_data)+8
        out.append((pos,end,len(raw)))
        pos=end+32
    return out

import os
def deflate_to_size(raw, target, pick=None):
    """raw-deflate stream of exactly `target` bytes that inflates to raw (padding with empty stored blocks)"""
    best=None; cands=[]
    pick=int(os.environ.get('WL_PICK','0')) if pick is None else pick
    for lvl in range(1,10):
        for mem in (8,9):
            for strat in (zlib.Z_DEFAULT_STRATEGY, zlib.Z_FILTERED):
                co=zlib.compressobj(lvl,zlib.DEFLATED,-15,mem,strat)
                z=co.compress(raw)+co.flush(zlib.Z_FULL_FLUSH)
                for fin in (b'\x03\x00', b'\x01\x00\x00\xff\xff'):
                    s=len(z)+len(fin)
                    pad=target-s
                    if pad>=0 and pad%5==0:
                        cand=z+b'\x00\x00\x00\xff\xff'*(pad//5)+fin
                        cands.append((pad,lvl,mem,strat,fin,cand))
    if not cands: raise ValueError('cannot reach exact size %d'%target)
    cands.sort(key=lambda x:x[:5])
    return cands[min(pick,len(cands)-1)][5]

def gz_member(raw, hdr, target_deflate_len=None):
    z=deflate_to_size(raw,target_deflate_len) if target_deflate_len else None
    if z is None:
        co=zlib.compressobj(int(os.environ.get('WL_LEVEL','9')),zlib.DEFLATED,-15); z=co.compress(raw)+co.flush()
    return hdr+z+struct.pack('<II',zlib.crc32(raw)&0xffffffff,len(raw)&0xffffffff)

def read_member(payload,pos):
    do=zlib.decompressobj(-15); raw=do.decompress(payload[pos+10:])
    end=len(payload)-len(do.unused_data)+8
    return raw,end
