"""vpdiff.py : viewport-on-sheet records (2026). prints new elements, plan-view edits and the position-dependent doubles of the Viewport element"""
import sys,os,struct; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab'))
import rvtgen,wledit
R=os.path.expanduser('~/rvt-research/rosetta/')
def load(fn): return rvtgen.Gen(R+fn)
sb=load('2026_sheet_viewport_base.rte'); sv=load('2026_sheet_viewport_var.rte')
ia=set(sb.e.m.ids); ib=set(sv.e.m.ids); new=sorted(ib-ia); print('NEW',[(i,sv.e.trace(i)[2]['class']) for i in new])
vp=[i for i in new if sv.e.trace(i)[2]['class']=='Viewport'][-1]; print('placed viewport id',vp)
t=sv.template(vp); print('viewport rec',len(t['rec']),'hdr',len(t['hdr']),'item',len(t['item']))
for n,o,e,v in t['log']:
    if 'Identifier' in n or n=='ElementId.m_id': continue
    print('  ',n,o,e,str(v)[:100])
# plan view edits
plan=[i for i in ia if sb.e.trace(i)[2]['class']=='DBViewPlan' and i>=303689]
for i in plan:
    a=sb.template(i); b=sv.template(i)
    for k in ('rec','hdr','item'):
        if a[k]!=b[k]: print('PLAN',i,k,len(a[k]),len(b[k]),[x for x in range(min(len(a[k]),len(b[k]))) if a[k][x]!=b[k][x]][:20])
# position pair
pb=load('2026_sheet_viewport_pos_base.rte'); pv=load('2026_sheet_viewport_pos_var.rte')
def placed(g,base):
    ids=sorted(set(g.e.m.ids)); c=[i for i in ids if i>=303689 and g.e.trace(i)[2]['class']=='Viewport']; return c
print('pos base vps',placed(pb,0)); print('pos var vps',placed(pv,0))
a=pb.template(placed(pb,0)[-1]) if False else None
