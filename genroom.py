"""genroom.py - merge N one-room LevelRoomPlan records (as made by genlib2.make_room) into ONE level plan for N disjoint rectangular rooms.
Layout learnt from Revit's own rooms_multi rosetta (rec): [188 B element+plan head][u32 nseg][nseg*124 PlanSegmentInfoPair][u32 ncirc][ncirc*144 PlanCircuit (area 8, envelope 32, id 4, sides u32+4*24)]
[u32 ncomp][comps: u32 n, n*u32 ids, outer u32, enclosing u32 (20 B for n=2)][u32 nrooms][8*nrooms][u32 unusedItems][u32 rbSeedCache].
Revit orders circuits in REVERSE room creation order (circuit ids 0.. follow that order), rooms and segments in creation order (verified on 2-, 3-room plans)."""
import struct
SEG0=188; SEG=124; CIRC=144; COMP=20
def split1(rec):
    """one-room plan -> (head, segs, circs, rooms) with offsets of the 4-segment layout"""
    n=struct.unpack_from('<I',rec,SEG0)[0]; assert n==4
    s1=SEG0+4+n*SEG; nc=struct.unpack_from('<I',rec,s1)[0]; assert nc==2
    c1=s1+4+nc*CIRC; nk=struct.unpack_from('<I',rec,c1)[0]; assert nk==1
    k1=c1+4+COMP; nr=struct.unpack_from('<I',rec,k1)[0]; assert nr==1
    return dict(head=rec[:SEG0],segs=rec[SEG0+4:s1],circs=[rec[s1+4+i*CIRC:s1+4+(i+1)*CIRC] for i in range(2)],room=struct.unpack_from('<Q',rec,k1+4)[0],tail=rec[k1+12:],end=k1+12+len(rec[k1+12:]))
def merge(recs):
    """recs: one-room plan records in room creation order -> merged plan record (unstamped)"""
    P=[split1(r) for r in recs]; N=len(P)
    out=bytearray(P[0]['head']); out+=struct.pack('<I',4*N)+b''.join(p['segs'] for p in P)
    out+=struct.pack('<I',2*N)
    for pos in range(N):
        j=N-1-pos
        for k,c in enumerate(P[j]['circs']):
            c=bytearray(c); struct.pack_into('<i',c,40,2*pos+k)
            # sides' circuit-id carry no other fields; copy as is
            out+=c
    out+=struct.pack('<I',N)
    for pos in range(N): out+=struct.pack('<IIIII',2,2*pos,2*pos+1,2*pos+1,0xffffffff)
    out+=struct.pack('<I',N)+b''.join(struct.pack('<Q',p['room']) for p in P)+P[0]['tail']
    return bytes(out)
def circuit_ids(N): return [2*(N-1-j) for j in range(N)]    # inner circuit id of room j
