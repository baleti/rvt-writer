import sys,os; sys.path.insert(0,os.path.expanduser('~/rvt-research/write-lab/campaign')); os.environ['STAGEB']='1'
import stages
r=stages.api_stage(int(sys.argv[1]),os.path.abspath(sys.argv[2]),sys.argv[4]=='1' if len(sys.argv)>4 else False,sys.argv[3])
print(sys.argv[2],'ok=%s err=%s cmp=%s'%(r['ok'],r.get('err'),r.get('cmp')),flush=True)
