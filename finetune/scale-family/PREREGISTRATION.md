# Pre-registration: does claim-checking transfer to a claim family it never saw? (+ a 3x larger real count test)

Written and committed **before** any training in this folder. Date: 2026-10-22 (America/Chicago).

## Why this, and why not a bigger model
The plan was to scale to Qwen2.5-1.5B/3B. A smoke test on the E2B CPU template (`smoke.py`, logged in
`my-sandboxes.txt`) showed it isn't feasible here. In fp32 it was killed for running out of memory at the 8 GB cap. In
bf16 it took 37 s per training step at 700 tokens and peaked at 7.6 GB. A 3-epoch run would take about 12 hours per seed.
A larger template is refused (8,192 MiB max). No new agent transcripts exist beyond the 388 already used, so a fresh
real set can't be mined. This round asks the most useful question that fits: **does it transfer across claim families?**

## Arms (Qwen2.5-0.5B, same LoRA / lr / 3 epochs / 400 balanced items / selection rule as ../realistic-count)
- **Held-out family (main):** training and validation contain **only test-runner claims** (vitest, etc.). No lint or
  typecheck claims at all. Same recipe as realistic-count otherwise (realistic count pairs, count/fail
  counterfactuals, wrong run held out). 4 seeds (0–3).
- **Control:** identical, but lint/typecheck claims from train sessions are allowed in training. 4 seeds.
- **Selection rule (unchanged):** best val balanced accuracy among epochs with val true-claim accuracy ≥ 0.95, else
  highest val true-claim accuracy.

## Eval sets
- **Family-eval:** 25 lint/typecheck items (12 true, 13 false: wrong-run and failed-run fakes) from sessions that
  appear in **no** training set of either arm (`family-eval-ids.json`). Primary.
- **Expanded real count:** the benchmark's own count recipe applied to **every** eligible real true claim in test
  sessions, giving 30 items (was 10). Real claim and real log, one number changed.
- Unchanged: 77-item test split (true claims, wrong run, count, fail), cue-stripped test.

## Hypotheses and pass thresholds (selected epoch, mean over 4 seeds)
- **F1, family transfer:** main arm on family-eval reaches balanced accuracy ≥ 0.80 and true-claim accuracy ≥ 0.90.
- **F2, transfer gap:** main arm balanced accuracy on family-eval is within 10 points of the control arm.
- **C1, real counting at scale:** main arm catches ≥ 0.50 of the 30 expanded real count fakes, with real true-claim
  accuracy ≥ 0.95.
Each is pass/fail. Per-seed numbers and session-bootstrap CIs will be reported, negative or not.

## Budget
Series cap raised to $40. Spend is tracked per sandbox from logged seconds at E2B list price. Runs are force-stopped
at 4,200 s.
