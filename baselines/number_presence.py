"""No-model baseline: a claim is 'supported' iff every number in its checked span appears as a numeric token
in the evidence (command + output excerpt). Usage: python baselines/number_presence.py [jsonl ...]"""
import json, re, subprocess, sys
NUM = re.compile(r'\d+(?:\.\d+)?')
def predict(item):
    log = ' '.join(e.get('command', '') + ' ' + e.get('output_excerpt', '') for e in item['evidence'])
    toks = set(NUM.findall(log))
    return 'supported' if all(n in toks for n in NUM.findall(item['checked_span'])) else 'unsupported'
def run(path):
    r = {'supported': [0, 0], 'unsupported': [0, 0]}
    for line in open(path):
        if line.strip():
            it = json.loads(line); r[it['label']][1] += 1; r[it['label']][0] += predict(it) == it['label']
    commit = subprocess.run(['git', 'log', '-1', '--format=%H', '--', path], capture_output=True, text=True).stdout.strip()
    c = sum(v[0] for v in r.values()); n = sum(v[1] for v in r.values())
    return {'file': path, 'input_commit': commit, 'correct': c, 'n': n,
            'true_claims_correct': r['supported'][0], 'true_claims_n': r['supported'][1],
            'fakes_caught': r['unsupported'][0], 'fakes_n': r['unsupported'][1]}
if __name__ == '__main__':
    paths = sys.argv[1:] or ['finetune/count-family/test-syn_heldfmt.jsonl', 'finetune/count-family/test-syn_trainfmt.jsonl']
    out = [run(p) for p in paths]
    json.dump(out, open('baselines/number_presence_results.json', 'w'), indent=2); print(json.dumps(out, indent=2))
