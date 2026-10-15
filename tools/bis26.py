#!/usr/bin/env python3
"""tools/bis26.py OUTDIR : 2026 bisect files on the house_base seed (does Revit refuse writer additions when no level is added?)"""
import sys,os; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL)
import scenes
D=sys.argv[1]; R=[(60,0),(100,0),(100,26),(60,26)]
def walls(S):
    for k in range(4): S.wall(R[k],R[(k+1)%4],10.0)
cases={'a_walls':lambda S:walls(S),
       'b_walls_level':lambda S:(S.level('L2',12.0),walls(S)),
       'c_level':lambda S:S.level('L2',12.0),
       'd_grid_level':lambda S:(S.level('L2',12.0),S.grid('GA',(60,-10),(60,40))),
       'e_level_walls':lambda S:(walls(S),S.level('L2',12.0)),
       'f_text':lambda S:S.text(60,-6,'note'),
       'g_floor':lambda S:S.floor(60,0,40,26),
       'h_col':lambda S:S.column_lv(64,3,355,S.level('L2',12.0)),
       'i_walls20':lambda S:[S.wall((60+k*3,0),(60+k*3,20),10.0) for k in range(20)],
       'j_text20':lambda S:[S.text(60+k*3,-6,'note %d'%k) for k in range(20)],
       'k_text80':lambda S:[S.text(60+k*3,-6,'note %d'%k) for k in range(80)],
       'l_plan':lambda S:S.planview(355,'Extra plan'),
       'n_text_floor':lambda S:(S.text(60,-6,'note'),S.floor(60,30,40,26)),
       'o_level_floor':lambda S:(S.level('L2',12.0),S.floor(60,30,40,26)),
       'p_rect_floor':lambda S:(walls(S),S.floor(60,30,40,26)),
       'q_text_walls20':lambda S:(S.text(60,-6,'note'),[S.wall((60+k*3,0),(60+k*3,20),10.0) for k in range(20)]),
       'r_floor_text':lambda S:(S.floor(60,30,40,26),S.text(60,-6,'note')),
       'm_walls_plan':lambda S:(walls(S),S.planview(355,'Extra plan'))}
for n,f in cases.items():
    if len(sys.argv)>2 and n not in sys.argv[2:]: continue
    S=scenes.Scene(n,2026); f(S); S.commit('%s/%s.rte'%(D,n)); print('built',n,S.counts)
