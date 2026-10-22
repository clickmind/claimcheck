# Smoke test in E2B: can Qwen2.5-1.5B LoRA train on the CPU template (memory, s/step)? Logs id; always kills.
import os,time
from e2b import Sandbox
H=os.path.dirname(os.path.abspath(__file__))
sb=Sandbox.create('claimcheck-ml',timeout=1800);t0=time.time();open(f'{H}/my-sandboxes.txt','a').write(f'{sb.sandbox_id} smoke-1.5b created {time.strftime("%H:%M:%S")}\n')
code='''
import torch,time,resource
from transformers import AutoTokenizer,AutoModelForCausalLM
from peft import LoraConfig,get_peft_model
for dt in (torch.bfloat16,):
  t=time.time();m=AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct",torch_dtype=dt)
  m=get_peft_model(m,LoraConfig(r=16,lora_alpha=32,target_modules=["q_proj","k_proj","v_proj","o_proj"],task_type="CAUSAL_LM"))
  opt=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=2e-4);x=torch.randint(0,1000,(1,700))
  for i in range(3):
    s=time.time();l=m(input_ids=x,labels=x).loss;l.backward();opt.step();opt.zero_grad();print(dt,"step",i,round(time.time()-s,1),"s maxrss GB",round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6,2),flush=True)
  with torch.no_grad():
    s=time.time();m(input_ids=x);print(dt,"fwd",round(time.time()-s,1),flush=True)
  del m,opt
'''
try:
  sb.files.write('/home/user/s.py',code);r=sb.commands.run('cd /home/user && python s.py > o.txt 2>&1; echo EXIT $?; dmesg 2>/dev/null | tail -3; tail -c 1500 o.txt; free -g',timeout=1500);print(r.stdout[-2000:])
except Exception as e: print('ERR',type(e).__name__,str(e)[:300])
finally: sb.kill();open(f'{H}/my-sandboxes.txt','a').write(f'{sb.sandbox_id} smoke-1.5b killed {time.strftime("%H:%M:%S")} after {int(time.time()-t0)}s\n')
