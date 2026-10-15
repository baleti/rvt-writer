"""Minimal Compound File Binary reader/writer that preserves the directory tree (names, ids, clsid, tree links, times).
Streams are replaced by id; everything is re-laid out contiguously. v3 (512) and v4 (4096) sectors."""
import struct
ENDOFCHAIN=0xFFFFFFFE; FREESECT=0xFFFFFFFF; FATSECT=0xFFFFFFFD; DIFSECT=0xFFFFFFFC; NOSTREAM=0xFFFFFFFF

class Entry:
    __slots__=('idx','name','type','color','left','right','child','clsid','state','ctime','mtime','start','size','data','raw')
class CFB:
    def __init__(self, buf):
        self.buf=buf; h=buf[:512]
        assert h[:8]==bytes.fromhex('d0cf11e0a1b11ae1')
        self.header=bytearray(h)
        (self.minor,self.major,bo,self.ssh,self.msh)=struct.unpack('<HHHHH',h[24:34])
        self.ss=1<<self.ssh; self.mss=1<<self.msh
        (nds,nfat,dstart,_,cutoff,mfstart,nmf,difstart,ndif)=struct.unpack('<IIIIIIIII',h[40:76])
        self.cutoff=cutoff
        fat_ids=list(struct.unpack('<109I',h[76:76+436]))
        s=difstart
        for _ in range(ndif):
            sec=self._sec(s); n=self.ss//4
            v=struct.unpack('<%dI'%n,sec); fat_ids+=list(v[:-1]); s=v[-1]
        fat_ids=[x for x in fat_ids if x!=FREESECT][:nfat]
        self.fat=[]
        for f in fat_ids: self.fat+=struct.unpack('<%dI'%(self.ss//4),self._sec(f))
        dirbuf=self._chain(dstart)
        self.entries=[]
        for i in range(len(dirbuf)//128):
            b=dirbuf[i*128:(i+1)*128]; e=Entry(); e.idx=i; e.raw=b
            nl=struct.unpack('<H',b[64:66])[0]
            e.name=b[:max(nl-2,0)].decode('utf-16le'); e.type=b[66]; e.color=b[67]
            e.left,e.right,e.child=struct.unpack('<III',b[68:80]); e.clsid=b[80:96]
            e.state=struct.unpack('<I',b[96:100])[0]; e.ctime=b[100:108]; e.mtime=b[108:116]
            e.start=struct.unpack('<I',b[116:120])[0]; e.size=struct.unpack('<Q',b[120:128])[0]
            if self.major==3: e.size&=0xFFFFFFFF
            e.data=None; self.entries.append(e)
        self.minifat=[]
        if mfstart!=ENDOFCHAIN:
            mb=self._chain(mfstart); self.minifat=list(struct.unpack('<%dI'%(len(mb)//4),mb))
        root=self.entries[0]; self.ministream=self._chain(root.start)[:root.size] if root.size else b''
        for e in self.entries:
            if e.type==2: e.data=self._read(e)
        self.nsectors=(len(buf)-512)//self.ss if self.major==3 else (len(buf)-4096)//self.ss
    def _sec(self,i):
        off=(i+1)*self.ss
        return self.buf[off:off+self.ss]
    def _chain(self,s):
        out=bytearray(); seen=0
        while s<0xFFFFFFFA:
            out+=self._sec(s); s=self.fat[s]; seen+=1
            assert seen<10**7
        return bytes(out)
    def _read(self,e):
        if e.size<self.cutoff:
            out=bytearray(); s=e.start
            while s<0xFFFFFFFA:
                out+=self.ministream[s*self.mss:(s+1)*self.mss]; s=self.minifat[s]
            return bytes(out[:e.size])
        return self._chain(e.start)[:e.size]
    def path(self,e):
        """full path of entry via tree walk"""
        return self._paths()[e.idx]
    def _paths(self):
        if hasattr(self,'_pp'): return self._pp
        pp={0:''}
        def walk(sid,prefix):
            st=[sid]
            while st:
                i=st.pop()
                if i==NOSTREAM: continue
                e=self.entries[i]; p=prefix+'/'+e.name; pp[i]=p
                st.append(e.left); st.append(e.right)
                if e.type==1 and e.child!=NOSTREAM: walk(e.child,p)
        walk(self.entries[0].child,'')
        self._pp=pp; return pp
    def streams(self):
        pp=self._paths(); return {pp[e.idx].lstrip('/'):e for e in self.entries if e.type==2 and e.idx in pp}

def write(cfbobj, path, v3_hint=None):
    """Serialise cfbobj with possibly modified e.data of stream entries."""
    c=cfbobj; ss=c.ss; mss=c.mss; ents=c.entries
    cutoff=c.cutoff
    # mini stream
    mini=bytearray(); minifat=[]
    for e in ents:
        if e.type==2:
            e.size=len(e.data)
            if e.size==0: e.start=ENDOFCHAIN
            elif e.size<cutoff:
                e.start=len(mini)//mss; n=(e.size+mss-1)//mss
                mini+=e.data+b'\0'*(n*mss-e.size)
                minifat+=list(range(e.start+1,e.start+n))+[ENDOFCHAIN]
    sectors=[]  # list of bytes objects (each ss long), plus bookkeeping
    fat=[]
    def alloc(data,fillto=None):
        n=(len(data)+ss-1)//ss; start=len(fat)
        fat.extend(list(range(start+1,start+n))+[ENDOFCHAIN] if n else [])
        pad=data+b'\0'*(n*ss-len(data)); 
        for i in range(n): sectors.append(pad[i*ss:(i+1)*ss])
        return start if n else ENDOFCHAIN
    for e in ents:
        if e.type==2 and e.size>=cutoff: e.start=alloc(e.data)
    root=ents[0]
    root.size=len(mini); root.start=alloc(bytes(mini)) if mini else ENDOFCHAIN
    mfdata=b''.join(struct.pack('<I',x) for x in minifat)
    mfstart=alloc(mfdata) if minifat else ENDOFCHAIN; nmf=(len(mfdata)+ss-1)//ss
    # directory
    db=bytearray()
    for e in ents:
        b=bytearray(e.raw)
        struct.pack_into('<I',b,116,e.start & 0xFFFFFFFF)
        struct.pack_into('<Q',b,120,e.size)
        db+=b
    while len(db)%ss: db+=b'\0'*128*0 + (b'\0'*128)   # pad with empty entries
    # unused entries must have left/right/child = NOSTREAM
    for i in range(len(ents),len(db)//128):
        o=i*128; db[o+68:o+80]=b'\xff'*12
    dstart=alloc(bytes(db)); ndirsec=len(db)//ss
    # FAT sectors (they describe themselves) + DIFAT
    per=ss//4
    nfat=0
    while True:
        total=len(fat)+nfat
        need=(total+per-1)//per
        ndif=max(0,(need-109+per-2)//(per-1)) if need>109 else 0
        need2=(len(fat)+need+ndif+per-1)//per
        if need2==need: break
        nfat=need2 if need2>nfat else need
        nfat=need2
    nfat=need
    # recompute with difat sectors
    while True:
        ndif=max(0,(nfat-109+per-2)//(per-1)) if nfat>109 else 0
        n2=(len(fat)+nfat+ndif+per-1)//per
        if n2==nfat: break
        nfat=n2
    fatstart=len(fat)
    fat+= [FATSECT]*nfat
    difstart=len(fat) if ndif else ENDOFCHAIN
    fat+= [DIFSECT]*ndif
    fat+= [FREESECT]*(nfat*per-len(fat))
    fatb=struct.pack('<%dI'%len(fat),*fat)
    for i in range(nfat): sectors.append(fatb[i*ss:(i+1)*ss])
    fat_ids=list(range(fatstart,fatstart+nfat))
    # DIFAT sectors
    rest=fat_ids[109:]
    for k in range(ndif):
        chunk=rest[k*(per-1):(k+1)*(per-1)]
        chunk+= [FREESECT]*(per-1-len(chunk))
        nxt=difstart+k+1 if k<ndif-1 else ENDOFCHAIN
        sectors.append(struct.pack('<%dI'%per,*chunk,nxt))
    h=bytearray(c.header)
    struct.pack_into('<I',h,40,ndirsec if c.major==4 else 0)
    struct.pack_into('<IIIIIIII',h,44,nfat,dstart,0,cutoff,mfstart,nmf,difstart,ndif)
    hd=(fat_ids[:109]+[FREESECT]*109)[:109]
    struct.pack_into('<109I',h,76,*hd)
    out=bytearray(h)
    if ss>512: out+=b'\0'*(ss-512)
    with open(path,'wb') as f:
        f.write(out)
        for s in sectors: f.write(s)
