import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,struct
f=sys.argv[1]; g=rvtgen.Gen(f)
for tid in map(int,sys.argv[2:]):
    t=g.template(tid); print('==',tid,t['cls'],'rec',len(t['rec']),'hdr',len(t['hdr']),'item',len(t['item']))
    print('HDR'); [print(' ',l) for l in t['hlog'] if 'Identifier' not in l[0] and l[0]!='ElementId.m_id']
    print('REC (non-id fields)'); [print(' ',l) for l in t['log'] if l[0] in ('Element.m_assocLevelId','InsertableInst.m_hostId','InsertableInst.m_hostParam','FamilyInstance.m_instOrigin','FamilyInstance.m_RefDir','FamilyInstance.m_zAxis','FamilyInstance.m_masterSymbolId','Trf.m_or','Trf.m_3x3','InstInfoBase.m_symbolId','FamilyInstance.m_structType','FamilyInstance.m_structUsage','FamilyInstance.m_roomBounding') or 'Outline' in l[0] or 'BBox' in l[0] or 'Bound' in l[0]]
