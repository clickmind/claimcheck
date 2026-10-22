# Seed-4 gate (Addendum F): INCOMPLETE. v2 was not scored.

Status, 2026-10-22 CT: **no PASS/FAIL for v2.** The single v2 run aborted on its first API call. The cause was an operator error: the caller was launched from `labeler/`, and the spend-log path `r6/spend/labeler-judge-spend.jsonl` is relative, so `log_call` raised FileNotFoundError *after* the call to row offset 945 returned. No label was written or seen. That one call is **not in the spend log**, and its cost is unknown (est. under $0.01; unverified). Per the no-rerun rule, v2 has not been rerun. A rerun needs an explicit decision from the Lead (or John), recorded as a deviation.

## Inputs (sha256 verified)
- WB labels `r6/audits/r6-seed4-audit-worldbuilder.jsonl` ac680985…a1c1 (from 0c8870a)
- Critic labels `r6/audits/r6-seed4-audit-critic.jsonl` 77b6f385…9b85 (9c0c938)
- `labeler/model_labeler_v2.py` 3b26a8e1…8c24, prompt 32bb48b1…82cc, blind sheet `labeler/seed4_blind.jsonl` 5a55a27c…9157
- Regex v3 output: `/workspace/claimcheck-lab/seed4-run/regex_v3.jsonl`, kept outside the repo because it contains target/eval fields

## Human-human (WB vs Critic), all 50 rows
- Claim kappa **0.878**, bootstrap 95% CI **[0.738, 1.0]** (2000 resamples, seed 0). Raw claim agreement 47/50. Gate agreement (claim + seen-contradicted) 47/50.
- **Gate threshold = 0.738** (CI lower bound; the fallback of 0.716 was not needed).
- Disagreements: 7713 (WB ambiguous / Critic claim+contradicts), 37775 (no_claim / claim), 40612 (ambiguous / claim+contradicts).
- WB: 17 claim, 2 ambiguous, 31 no_claim, 0 contradicted. Critic: 20 claim, 30 no_claim, 2 contradicts.

## Adjudicated (weaker label wins, C3)
- 17 claim, 2 ambiguous, 31 no_claim. Seen-contradicted: **0** of 17 claim rows (Wilson [0.0, 0.184]). Seen-contradicted limit for systems: ≤ 2.

## Regex v3 baseline: would FAIL the primary gate
- Claim kappa vs adjudicated **0.692** (< 0.738). Raw vs adjudicated 41/50, vs WB 41/50, vs Critic 43/50. Seen-contradicted on adjudicated claim rows: 1 (≤ 2, OK).
- 9 disagreements, each counted once: claim 7713, 37775, 38265, 40612, 56497, 66633, 75021, 79410; seen-contradicted 34304.

## v2 / hybrid
NOT RUN (see the status above). The hybrid needs v2 outputs.

Script: `r6/score_seed4.py`. Output: `r6/audits/seed4-score.json`.
