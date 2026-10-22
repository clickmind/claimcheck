# Generates World episodes in an E2B sandbox this script creates; logs id; always kills. Usage: python gen_e2b.py TAG N SEED
import sys,os,time
from e2b import Sandbox
tag,n,seed=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]);H=os.path.dirname(os.path.abspath(__file__))
sb=Sandbox.create('claimcheck-ml',timeout=3600);t0=time.time();open(f'{H}/my-sandboxes.txt','a').write(f'{sb.sandbox_id} {tag} created {time.strftime("%H:%M:%S")}\n')
try:
  sb.files.write('/home/user/world.py',open(f'{H}/world.py','rb').read())
  r=sb.commands.run('cd /home/user && curl -sL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-x64.tar.xz | tar xJ && pip install -q pytest >/dev/null 2>&1; echo ok',timeout=600);print(r.stdout[-200:],flush=True)
  sb.commands.run(f'cd /home/user && export PATH=/home/user/node-v20.18.0-linux-x64/bin:$PATH && python world.py {n} {seed} > eps.jsonl 2> err.txt',background=True,timeout=0)
  while True:
    time.sleep(45)
    try:
      sb.set_timeout(3600);c=sb.commands.run('wc -l < /home/user/eps.jsonl; tail -c 300 /home/user/err.txt; pgrep -f world.py >/dev/null && echo RUN || echo END',timeout=60).stdout
    except Exception as e: print('poll err',type(e).__name__,flush=True);continue
    print(tag,int(time.time()-t0),'s |',c.replace('\n',' ')[-200:],flush=True)
    if c.strip().endswith('END') or time.time()-t0>3300: break
  for k in range(5):
    try: open(f'{H}/eps-{tag}.jsonl','w').write(sb.files.read('/home/user/eps.jsonl'));break
    except Exception: time.sleep(10)
finally:
  sb.kill();open(f'{H}/my-sandboxes.txt','a').write(f'{sb.sandbox_id} {tag} killed {time.strftime("%H:%M:%S")} after {int(time.time()-t0)}s\n')
