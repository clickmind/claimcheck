# ClaimCheck spend ledger (updated 2026-10-22 ~09:05 CT)
The **hard $100 E2B cap** (John via Cos, Oct 22) covers **E2B sandbox spend only**. xAI model-API spend is a separate line, outside the cap.
Rate: $0.0001483/s (≈$0.53 per sandbox-hour), from R3's own $2.04 / 13,754 s at list price.
**Every E2B figure here is an estimate from logged seconds at list price. The actual total is in the E2B Console.**

## E2B headline
- **Series estimate: $13.4–14.5 at list price** (derivation below). **Worst case used for gating: $14.50.**
- **Reserve: $10. Gate for new rounds: $100 − $14.50 − $10 = $75.50.**
- All sandboxes have a kill line (43 created / 43 killed across 5 logs, checked at origin/main 8079320). None are open, so the open-sandbox worst-case line is gone.
- The $8.18 figure reported to the Scribe has an unverified source and isn't used.

## E2B by round
| Round | Sandboxes | Seconds | Cost | Basis / source |
|---|---|---|---|---|
| First LoRA fine-tune (d1e34ff) | 1 | ≥872 | **≥$0.13** | lower bound: script runtime, `finetune/out-q05/meta.json` "seconds" (no sandbox log) |
| Left-out-recipe + 2 seeds (96f788c) | 5 | ≥3,344 | **≥$0.50** | lower bound: script runtimes 803+604+577+658+702 s, `finetune/out-{loro-count,loro-fail,loro-swap,seed1,seed2}/meta.json` (no sandbox log) |
| Counterfactual (fa2aed9) | 22 | 34,980 | $5.19 | `finetune/counterfactual/my-sandboxes.txt` |
| Count family R3 (724de33) | 4 | 13,754 | $2.04 | `finetune/count-family/my-sandboxes.txt` |
| Realistic count R4 (00329d1) | 4 | 12,435 | $1.84 | `finetune/realistic-count/my-sandboxes.txt` |
| Family transfer + 1.5B smoke tests: 9 logged runs (6 training, 3 smoke) | 9 | 19,738 | $2.93 | `finetune/scale-family/my-sandboxes.txt` |
| Family transfer m0, c2 (ended by E2B 1 h limit) | 2 | UNKNOWN, ≤~3,600 each | $0.74–1.10 (README) | kill lines say "sandbox not found"; README @00329d1 |
| World probe | 1 | 12 | $0.00 | `finetune/world/my-sandboxes.txt` |
| World smoke (orphaned, killed by id) | 1 | ~458 (08:05:45→08:13:23) | ~$0.07 | timestamps in `finetune/world/my-sandboxes.txt`, no "after Ns" |
| **Sum** | 49 | | **≈ $13.44–13.80** | lower bounds included at their floor |
The 1.5B smoke tests (3 runs, 529 s, $0.08) are inside the family-transfer row. The $14.50 worst case adds margin over $13.80 for the two lower-bound rows and unbilled startup time.

## xAI model API (outside the cap)
- **$6.36** (per John via Cos, 08:17 CT). The README's "about" figures sum to ≈$6.59, and the v1 stalled attempt is **UNKNOWN**.

## Reconciliation
The Scribe's earlier ~$13.8 was E2B + API combined ($7.31 + $6.36, before R4 posted). It's superseded by the estimate above.
