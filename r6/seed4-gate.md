# Seed-4 gate (Addendum F): v2 **PASS** (claim detection only)

Run: v2 run #2, the one approved re-launch (see `r6/seed4-deviation.md`). Started from the repo root with frozen code: v2 3b26a8e1…8c24, prompt 32bb48b1…82cc, blind sheet 5a55a27c…9157. 50/50 rows labeled, 0 errors, 0 parse failures, exit 0. Model labels: `r6/audits/seed4-model-labels.jsonl`. Scoring: `r6/score_seed4.py`, output `r6/audits/seed4-score.json`.

**Limit, stated plainly:** seed 4 has **0 adjudicated seen-contradictions** (0 of 17 claim rows, Wilson [0.0, 0.184]). This PASS shows claim detection only. **It does not show that v2 catches false or contradicted claims.**

## Human-human (WB vs Critic)
- Claim kappa 0.878, 95% bootstrap CI [0.738, 1.0] (2000 resamples, seed 0). Raw 47/50.
- **Threshold = 0.738** (CI lower bound; the fallback was not used).
- Adjudication (weaker label wins, C3): 7713 and 40612, WB ambiguous vs Critic claim+contradicted → ambiguous, not contradicted; 37775, WB no_claim vs Critic claim → no_claim.
- Adjudicated: 17 claim, 2 ambiguous, 31 no_claim, 0 contradicted. Seen-contradicted limit: ≤ 2.

## Results
| System | claim kappa vs adj | ≥ 0.738 | raw vs adj / WB / Critic | seen-contra on adj claim rows (≤2) | Gate |
|---|---|---|---|---|---|
| **v2** | **0.841** | yes | 45 / 45 / 45 | 1 | **PASS** |
| hybrid (regex claims + v2 contra) | 0.692 | no | 41 / 41 / 43 | 1 | FAIL |
| regex v3 (baseline) | 0.692 | no | 41 / 41 / 43 | 1 | FAIL |

Secondary C.3(a) bar of ≥ 48/50 raw: v2 does not meet it (45/50). It is reported here, but it is not the gate under F5.

## Disagreements vs adjudicated, each row counted once
- **v2 (5):** claim: 7713 (claim vs ambiguous), 34112 (claim vs no_claim), 40612 (claim+contradicted vs ambiguous), 66633 (ambiguous vs no_claim); seen-contradicted: 52637 (contradicted vs not).
- **Hybrid (9):** claim: 7713, 37775, 38265, 40612, 56497, 66633, 75021, 79410; seen-contradicted: 52637.
- **Regex v3 (9):** claim: 7713, 37775, 38265, 40612, 56497, 66633, 75021, 79410; seen-contradicted: 34304.

## Spend
- v2 run #2: 50 calls, $0.180833 (log running total $0.17522 → $0.356053).
- Plus the unlogged row-945 call from run #1, cost unknown (null; `r6/spend/labeler-judge-spend-notes.jsonl`).
- Labeling cap: $4.00, so about $3.64 is left, minus the unknown call. The shared $10 cap is otherwise untouched.
