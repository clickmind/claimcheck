# ClaimCheck spend ledger (draft, 2026-10-22 ~08:20 CT)
The $40 hard cap covers **E2B sandbox spend only**. xAI model-API spend is a separate line, outside the cap.
E2B rate: R3's own figure, $2.04 / 13,754 s = **$0.0001483/s (≈$0.53 per sandbox-hour)**. Seconds come from the kill lines in each `my-sandboxes.txt`.

## E2B headline
- **Logged so far (from the sandbox logs): $7.31.**
- **Worst-case remaining: $40 − $7.31 − $8.10 (13 open R4 sandboxes × 4,200 s) = $24.59**, before the UNKNOWN rounds below.
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
$7.31 E2B + $6.36 API = **$13.67** ≈ $13.8. The Scribe's figure combines both lines. Only E2B counts against the $40 cap.
