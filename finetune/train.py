# LoRA fine-tune a small instruct model as a ClaimCheck claim checker. CPU-friendly.
# Usage: python train.py --model Qwen/Qwen2.5-0.5B-Instruct --epochs 3 --out out/
import json,argparse,random,time,math,torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from peft import LoraConfig,get_peft_model
ap=argparse.ArgumentParser();ap.add_argument('--model',default='Qwen/Qwen2.5-0.5B-Instruct');ap.add_argument('--epochs',type=int,default=3)
ap.add_argument('--lr',type=float,default=2e-4);ap.add_argument('--maxlen',type=int,default=768);ap.add_argument('--out',default='out');ap.add_argument('--seed',type=int,default=0)
a=ap.parse_args();torch.manual_seed(a.seed);random.seed(a.seed);torch.set_num_threads(max(1,torch.get_num_threads()))
items=[json.loads(l) for l in open('claims.jsonl')];split=json.load(open('split.json'))
tr=[i for i in items if split[i['id']]['split']=='train'];te=[i for i in items if split[i['id']]['split']=='test']
tok=AutoTokenizer.from_pretrained(a.model);m=AutoModelForCausalLM.from_pretrained(a.model,torch_dtype=torch.float32)
SYS=('You check one claim from a coding agent against its own logs. Judge only the CHECKED SPAN. Answer "supported" only if the evidence shows a run of '
 'the same check (same file/command if named) that exited 0 with no failures and every number in the span matches the output. Otherwise answer "unsupported". Reply with one word.')
def ev(i):
  s='\n---\n'.join(f"$ {e['command'][:200]}\n[exit {e['exit_code']}]\n{e['output_excerpt'][-700:]}" for e in i['evidence']) or '(none)'
  return s+('\n'+i['evidence_note'] if i['evidence_note'] else '')
def prompt_ids(i):
  body=f"CHECKED SPAN:\n{i['checked_span'][:400]}\n\nEVIDENCE:\n"
  e=tok(ev(i))['input_ids']
  for _ in range(4):
    msgs=[{'role':'system','content':SYS},{'role':'user','content':body+tok.decode(e)}]
    ids=tok.apply_chat_template(msgs,add_generation_prompt=True)
    if len(ids)<=a.maxlen: return ids
    e=e[-(len(e)-(len(ids)-a.maxlen)-8):]   # keep the END of the log (summary lines)
  return ids[-a.maxlen:]
A={'supported':tok(' supported'.strip())['input_ids'],'unsupported':tok('unsupported')['input_ids']}
@torch.no_grad()
def score(model,i):  # log P(answer) for each label, summed over its tokens
  p=prompt_ids(i);out={}
  for k,t in A.items():
    x=torch.tensor([p+t]);lg=model(x).logits[0,len(p)-1:-1].log_softmax(-1)
    out[k]=float(sum(lg[j,t[j]] for j in range(len(t))))
  return out
def evaluate(model,tag):
  model.eval();res=[]
  for i in te:
    s=score(model,i);res.append({'id':i['id'],'origin':i['origin'],'kind':i['kind'],'gold':'supported' if i['label']=='supported' else 'unsupported','margin':s['supported']-s['unsupported']})
  json.dump(res,open(f'{a.out}/pred-{tag}.json','w'),indent=0);return res
import os;os.makedirs(a.out,exist_ok=True);t0=time.time()
zs=evaluate(m,'zeroshot');print('zeroshot done',round(time.time()-t0),flush=True)
m=get_peft_model(m,LoraConfig(r=16,lora_alpha=32,lora_dropout=0.05,target_modules=['q_proj','k_proj','v_proj','o_proj'],task_type='CAUSAL_LM'))
opt=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=a.lr)
data=[(prompt_ids(i),A['supported' if i['label']=='supported' else 'unsupported']) for i in tr]
steps=a.epochs*len(data);n=0;log=[]
for ep in range(a.epochs):
  random.shuffle(data);m.train();tl=0
  for p,t in data:
    x=torch.tensor([p+t]);lab=torch.tensor([[-100]*len(p)+t])
    lr=a.lr*0.5*(1+math.cos(math.pi*n/steps));[g.__setitem__('lr',lr) for g in opt.param_groups]
    loss=m(input_ids=x,labels=lab).loss;loss.backward();opt.step();opt.zero_grad();tl+=loss.item();n+=1
  log.append({'epoch':ep+1,'train_loss':tl/len(data)});print(log[-1],round(time.time()-t0),flush=True)
ft=evaluate(m,'finetuned')
json.dump({'model':a.model,'epochs':a.epochs,'lr':a.lr,'maxlen':a.maxlen,'lora':{'r':16,'alpha':32,'targets':'q,k,v,o'},'n_train':len(tr),'n_test':len(te),'train_log':log,'seconds':round(time.time()-t0)},open(f'{a.out}/meta.json','w'),indent=1)
print('done',round(time.time()-t0))
