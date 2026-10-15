#!/usr/bin/env python3
"""grid_min.py SEED YEAR OUT : add ONE exact grid clone (no scene machinery) to SEED (to test seed dependence)"""
import sys,os,struct; WL=os.path.expanduser('~/rvt-research/write-lab'); sys.path.insert(0,WL)
import rvtgen,genlib2,genlib
seed,year,out=sys.argv[1],int(sys.argv[2]),sys.argv[3]; genlib2.YEAR=year
T=genlib2.grid_template(rvtgen.Gen(os.path.expanduser('~/rvt-research/rosetta/%d_grid_level_base.rte'%year)))
g=rvtgen.Gen(seed)
import scenes
tr=scenes.trip(g); nid=g.nextid; g.nextid+=1
hd,rec,it,row=genlib2.make_grid(g,T,nid,'G2',(10,-5),(10,25),tr)
g.new.append((hd,rec,it,nid)); g.rows.append(row)
g.itag=T['item'][16:18]
g.latest_edits=[('Latest',lambda raw:genlib2.set_last_grid_name(genlib2.grid_registry(raw,genlib2.grid_anchors(year),[nid]),'G2'))]
g.commit(out); print('wrote',out,nid)
