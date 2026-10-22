# Runs train2.py in an E2B sandbox this script creates, logs its id, always kills it. Reads E2B_API_KEY from env (never printed).
# Usage: python run_e2b2.py TAG [train2.py args...]
import sys,os,time
from e2b import Sandbox
tag=sys.argv[1];MAXS=int(os.environ.get('MAXS','4200'));extra=' '.join(sys.argv[2:]);H=os.path.dirname(os.path.abspath(__file__))
sb=Sandbox.create('claimcheck-ml',timeout=3600);t0=time.time()
open(f'{H}/my-sandboxes.txt','a').write(f'{sb.sandbox_id} {tag} created {time.strftime("%H:%M:%S")}\n');print('sandbox',sb.sandbox_id,flush=True)
def rd(p):
  for k in range(5):
    try: return sb.files.read(p)
    except Exception: time.sleep(10)
  raise RuntimeError('read failed '+p)
try:
  for f in ['train3.py','train.jsonl','train-ctrl.jsonl','val.jsonl','test-masked.jsonl','test-syn_heldfmt.jsonl','test-syn_trainfmt.jsonl','test-family.jsonl','test-xcount.jsonl','../split.json','../../data/claims.jsonl']:
    sb.files.write('/home/user/w/'+os.path.basename(f),open(f'{H}/{f}','rb').read())
  sb.commands.run(f'cd /home/user/w && python train3.py --out out {extra} > log.txt 2>&1',background=True,timeout=0)
  while True:
    time.sleep(60)
    try: sb.set_timeout(3600);lg=sb.files.read('/home/user/w/log.txt').strip();last=lg.splitlines()[-1] if lg else ''
    except Exception as e: print(tag,'poll error (retrying):',type(e).__name__,flush=True);continue
    print(tag,int(time.time()-t0),'s |',last[:160],flush=True)
    if last.startswith('done ') or 'Traceback' in lg or time.time()-t0>MAXS: break
  os.makedirs(f'{H}/out-{tag}',exist_ok=True)
  names=[f'pred-ep{e}-{k}.json' for e in (1,2,3) for k in ('val','test','test-masked','syn_heldfmt','syn_trainfmt','family','xcount')]+['pred-zeroshot.json','meta.json','log.txt']
  for f in names:
    try: open(f'{H}/out-{tag}/{f}','w').write(rd(f'/home/user/w/out/{f}' if f!='log.txt' else '/home/user/w/log.txt'))
    except Exception: pass
finally:
  sb.kill();open(f'{H}/my-sandboxes.txt','a').write(f'{sb.sandbox_id} {tag} killed {time.strftime("%H:%M:%S")} after {int(time.time()-t0)}s\n')
