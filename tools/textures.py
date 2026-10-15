#!/usr/bin/env python3
"""tools/textures.py : copy the Autodesk material library texture folders 1/ and 2/ (all corpus refs are 1/Mats/...) from the offline Revit VM to ~/.cache/rvt-textures (local only, never publish) + INDEX.tsv"""
import sys,os,zipfile,struct; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL+'/campaign'); import guest
D=os.path.expanduser('~/.cache/rvt-textures'); os.makedirs(D,exist_ok=True)
T=r'C:\Program Files (x86)\Common Files\Autodesk Shared\Materials\Textures'
with guest.vmlock():
    for sub in ('1','2'):
        print(guest.script(r'''Compress-Archive -Path "%s\%s" -DestinationPath "C:\wl\out\tex%s.zip" -CompressionLevel NoCompression -Force; (Get-Item "C:\wl\out\tex%s.zip").Length'''%(T,sub,sub,sub),1800))
        z='/tmp/claude-1000/tex%s.zip'%sub; guest.get(r'C:/wl/out/tex%s.zip'%sub,z,1800); zipfile.ZipFile(z).extractall(D); os.remove(z)
        guest.script(r'Remove-Item "C:\wl\out\tex%s.zip"'%sub,60)
def size(p):
    b=open(p,'rb').read(64*1024)
    try:
        if b[:8]==b'\x89PNG\r\n\x1a\n': return struct.unpack('>II',b[16:24])
        if b[:2]==b'\xff\xd8':
            i=2
            while i<len(b)-9:
                if b[i]!=0xff: i+=1; continue
                m=b[i+1]
                if m in (0xc0,0xc1,0xc2): h,w=struct.unpack('>HH',b[i+5:i+9]); return w,h
                i+=2+struct.unpack('>H',b[i+2:i+4])[0]
    except Exception: pass
    return ('','')
with open(D+'/INDEX.tsv','w') as f:
    f.write('# source: Autodesk material library textures (Autodesk Shared\\Materials\\Textures, folders 1 and 2; folder 3 = 2.2 GB high-res set not copied), offline Revit VM on host2 (Revit 2020-2026 installs). LOCAL USE ONLY.\npath\tbytes\twidth\theight\n')
    for r,_,fs in os.walk(D):
        for fn in sorted(fs):
            p=os.path.join(r,fn); rel=os.path.relpath(p,D)
            if rel=='INDEX.tsv': continue
            w,h=size(p); f.write('%s\t%d\t%s\t%s\n'%(rel,os.path.getsize(p),w,h))
print('done',D)
