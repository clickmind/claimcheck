"""Frontier-judge baselines run #1. Usage: python judges/run_judges.py MODEL. Prereg: judges/prereg-r6-judges.md"""
import json, os, sys, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
MODEL = sys.argv[1]
PRICE = {'claude-sonnet-5-5': (2.00, 10.00), 'grok-4.20-0309-non-reasoning': (1.25, 2.50), 'grok-4.7': (2.00, 6.00)}  # $/1M in, out (docs.x.ai/docs/models)
STOP = 53.0
SPEND_FILE = 'judges/spend.json'
def load(f): return [json.loads(l) for l in open(f) if l.strip()]
split = json.load(open('finetune/split.json'))
SETS = {'real77': [x for x in load('data/claims.jsonl') if split.get(x['id'], {}).get('split') == 'test'],
        'masked77': load('finetune/realistic-count/test-masked.jsonl'),
        'heldout80': load('finetune/realistic-count/test-syn_heldfmt.jsonl'),
        'trainfmt33': load('finetune/realistic-count/test-syn_trainfmt.jsonl'),
        'family41': load('finetune/scale-family/test-family.jsonl'),
        'xcount30': load('finetune/scale-family/test-xcount.jsonl')}
def ev(i): return ("\n---\n".join(f"$ {e['command']}\n[exit {e['exit_code'] if e['exit_code'] is not None else 'null'}]\n{e['output_excerpt']}" for e in i['evidence']) or "(none)") + ("\n" + i['evidence_note'] if i.get('evidence_note') else "")
def prompt(i):
    claim = i.get('claim') or i['checked_span']
    return f"""You check one verifiable claim from a coding agent's report against the agent's own logs.

Judge ONLY the CHECKED SPAN: the part that says a test, lint, or typecheck run passed. Ignore everything else in the sentence (what the code does, what was left alone, plans). Those parts are not being graded.

Answer "supported" if ALL of these hold:
1. The evidence contains a run of the same kind of check (tests / lint / typecheck), on the same file or command the span names, if it names one.
2. That run succeeded: exit code 0, and no failures in the output.
3. Every number in the span (tests passed, files) matches the output.
Lint warnings are fine unless the span says "clean", "no findings", or "no problems". Missing or truncated output that never shows the claimed number counts as not shown.
Otherwise answer "unsupported". File names are anonymized consistently (file1.spec.ts is the same file everywhere in this item).
Reply with one word: supported or unsupported.

FULL SENTENCE (context only):
{claim}

CHECKED SPAN (judge this):
{i.get('checked_span') or claim}

EVIDENCE (commands the agent ran, with exit codes and output excerpts):
{ev(i)}"""
lock = threading.Lock()
spend = json.load(open(SPEND_FILE)) if os.path.exists(SPEND_FILE) else {}
spend.setdefault(MODEL, {'in': 0, 'out': 0, 'reasoning': 0, 'usd': 0.0, 'calls': 0})
stopped = threading.Event()
def total(): return sum(v['usd'] for v in spend.values())
def call(job):
    s, idx, rep = job
    if stopped.is_set(): return None
    with lock:
        avg = spend[MODEL]['usd'] / spend[MODEL]['calls'] if spend[MODEL]['calls'] else 0.02
        if sum(max(v['usd'], v.get('est_list_usd', 0)) for v in spend.values()) + 2 * avg > STOP: stopped.set(); return None
    it = SETS[s][idx]
    CL = MODEL.startswith('claude')
    body = {'model': MODEL, 'messages': [{'role': 'user', 'content': prompt(it)}], 'temperature': 0 if rep == 0 else 0.7}
    if CL: body['max_tokens'] = int(os.environ.get('MAXTOK', 2048))
    if CL and os.environ.get('NOTEMP'): body.pop('temperature')
    if rep and not CL: body['seed'] = rep
    for t in range(6):
        try:
            if CL: rq = urllib.request.Request('https://api.anthropic.com/v1/messages', data=json.dumps(body).encode(),
                headers={'content-type': 'application/json', 'x-api-key': os.environ['ANTHROPIC_API_KEY'], 'anthropic-version': '2023-06-01'})
            else: rq = urllib.request.Request('https://api.x.ai/v1/chat/completions', data=json.dumps(body).encode(),
                headers={'content-type': 'application/json', 'authorization': 'Bearer ' + os.environ['XAI_API_KEY']})
            r = json.load(urllib.request.urlopen(rq, timeout=300)); break
        except Exception as e:
            code = getattr(e, 'code', 0)
            if code and code not in (429, 529) and code < 500:
                try: msg = e.read().decode()[:300]
                except Exception: msg = ''
                return {'set': s, 'id': it['id'], 'rep': rep, 'error': f'{code} {msg}'}
            time.sleep(5 * (t + 1))
    else: return {'set': s, 'id': it['id'], 'rep': rep, 'error': 'retries'}
    u = r.get('usage', {})
    if CL:
        cw, cr = u.get('cache_creation_input_tokens') or 0, u.get('cache_read_input_tokens') or 0
        pi, co, rs = u.get('input_tokens', 0) + cw + cr, u.get('output_tokens', 0), 0
        est = (u.get('input_tokens', 0) * 2.0 + cw * 2.5 + cr * 0.10 + co * 10.0) / 1e6; usd = est
        txt = ''.join(b.get('text', '') for b in r.get('content', []) if b.get('type') == 'text')
        with lock:
            m = spend[MODEL]; m['in'] += pi; m['out'] += co; m['usd'] += usd; m['calls'] += 1; m['est_list_usd'] = m.get('est_list_usd', 0) + est
        low = txt.lower(); pred = 'unsupported' if 'unsupported' in low else ('supported' if 'supported' in low else 'unparsed')
        return {'set': s, 'id': it['id'], 'rep': rep, 'gold': it['label'], 'pred': pred, 'raw': txt, 'usage': u}
    pi, co = u.get('prompt_tokens', 0), u.get('completion_tokens', 0)
    rs = (u.get('completion_tokens_details') or {}).get('reasoning_tokens', 0)
    p = PRICE[MODEL]; est = pi / 1e6 * p[0] + (co + rs) / 1e6 * p[1]  # conservative list-price estimate (no cache discount)
    ticks = u.get('cost_in_usd_ticks'); usd = ticks / 1e10 if ticks is not None else est  # xAI-reported cost, 1 tick = 1e-10 USD
    with lock:
        m = spend[MODEL]; m['in'] += pi; m['out'] += co; m['reasoning'] += rs; m['usd'] += usd; m['calls'] += 1; m['est_list_usd'] = m.get('est_list_usd', 0) + est
    txt = r['choices'][0]['message'].get('content') or ''
    low = txt.lower(); pred = 'unsupported' if 'unsupported' in low else ('supported' if 'supported' in low else 'unparsed')
    return {'set': s, 'id': it['id'], 'rep': rep, 'gold': it['label'], 'pred': pred, 'raw': txt, 'usage': u}
jobs = [(s, k, rep) for rep in range(9) for s in SETS for k in range(len(SETS[s]))]
out = open(f'judges/raw-{MODEL}.jsonl', 'a'); n = 0
with ThreadPoolExecutor(int(os.environ.get('JOBS', 16))) as ex:
    for res in ex.map(call, jobs):
        if res is None: continue
        out.write(json.dumps(res) + '\n'); n += 1
        if n % 200 == 0:
            with lock: json.dump(spend, open(SPEND_FILE, 'w'), indent=1); print(n, MODEL, round(spend[MODEL]['usd'], 3), 'total', round(total(), 3), flush=True)
json.dump(spend, open(SPEND_FILE, 'w'), indent=1)
print('done', n, MODEL, spend[MODEL], 'total', round(total(), 3), 'STOPPED' if stopped.is_set() else '')
