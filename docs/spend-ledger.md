# ClaimCheck spend ledger (draft, 2026-10-22 ~08:20 CT)
The **hard $100 E2B cap** (John via Cos, Oct 22; was $40) covers **E2B sandbox spend only**. xAI model-API spend is a separate line, outside the cap.
E2B rate: R3's own figure, $2.04 / 13,754 s = **$0.0001483/s (≈$0.53 per sandbox-hour)**. Seconds come from the kill lines in each `my-sandboxes.txt`.

## E2B headline
- **Logged so far (from the sandbox logs): $7.31.**
- **Worst-case remaining: $100 − $7.31 − $8.10 (13 open R4 sandboxes × 4,200 s) = $84.59**, before the UNKNOWN rounds below.
- **Reserve: $10. Spend gate (worst case − reserve): $74.59**, before the UNKNOWN rounds. No round starts if its ceiling exceeds what is left of the gate.
- **Total E2B spend: unknown until R4 pulls E2B's own usage data.**
- $8.18 was reported to the Scribe; **source unverified**. It is $0.87 above the logged $7.31. Possible causes: the UNKNOWN rounds, or accrual on open sandboxes. Not confirmed.

## E2B: logged
| Round | Sandboxes (killed) | Seconds | Rate $/s | Cost | Source file |
|---|---|---|---|---|---|
| First LoRA fine-tune (d1e34ff) | UNKNOWN | UNKNOWN | - | **UNKNOWN** | no sandbox log located (not verified) |
| Left-out-recipe round (96f788c) | UNKNOWN | UNKNOWN | - | **UNKNOWN** | no sandbox log located (not verified) |
| Counterfactual (fa2aed9) | 22 | 34,980 | 0.0001483 | $5.19 (README ~$5.20) | finetune/counterfactual/my-sandboxes.txt |
| Count family R3 (724de33) | 4 | 13,754 | 0.0001483 | $2.04 | finetune/count-family/my-sandboxes.txt |
| 1.5B smoke tests | 3 | 529 | 0.0001483 | $0.08 | finetune/scale-family/my-sandboxes.txt |
| World probe | 1 | 12 | 0.0001483 | $0.00 | finetune/world/my-sandboxes.txt |
| **Logged so far** | 30 | 49,275 | | **$7.31** | |

## E2B: pending (no kill line; counted at the 4,200 s force-stop)
| Folder | Open | Created (CT) | Worst-case s | Worst-case $ |
|---|---|---|---|---|
| realistic-count | 4 | 07:29 | 16,800 | $2.49 |
| scale-family m0–3, c0–3 | 8 | 07:44 | 33,600 | $4.98 |
| world smoke | 1 | 08:05 | 4,200 | $0.62 |
| **Pending worst case** | 13 | | 54,600 | **$8.10** |

## xAI model API (outside the cap)
- **$6.36** (per John via Cos, 08:17 CT).
- The README's own "about" figures sum to ≈$6.59: v1.2 $1.54, v1.1 ×2 ~$3.40, v1 ~$1.65. On top of that, the v1 stalled attempt is **UNKNOWN** ("unlogged spend").

## Reconciliation with the Scribe's ~$13.8
$7.31 E2B + $6.36 API = **$13.67** ≈ $13.8. The Scribe's figure combines both lines. Only E2B counts against the $100 cap.

## Model API: judges run #1 (2026-10-22, approved by John 09:05 CT, cap $55)
| Model | Calls | In tok | Reasoning tok | $ (xAI-reported) | $ list est. | Source |
|---|---|---|---|---|---|---|
| grok-4.20-0309-non-reasoning | 3,042 | 1,812,420 | 0 | 0.86 | 2.34 | judges/spend.json |
| grok-4.7 | 3,042 | 5,046,084 | 1,357,817 | 11.28 | 18.26 | judges/spend.json |
| claude-sonnet-5-5 | 3,042 | 1,957,599 | - | 7.84 | 7.84 | judges/spend.json (usage × list, Anthropic) |
| **Total** | | | | **19.98** | 28.43 | plus ~$0.0001 xAI smoke call and 2 tiny Claude test calls |
