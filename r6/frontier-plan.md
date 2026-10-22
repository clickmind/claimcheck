# ClaimCheck frontier plan (r6)

**Goal** (John, 15:21 CT Oct 22 2026, via Cos): push to the frontier and ship something the AI community can actually use, not just a paper result.
**Caps (unchanged):** E2B $100 for the series (about $13.80 spent so far, per Lead). grok-4.20 judge/labeler $10 total, with labeling ≤ $4. Every run is pre-registered (a committed addendum) before it starts. Nothing goes public without John, and Cos publishes. References: `r6/refs.md` (numbered [#n] below). All costs and dates below are **estimates** unless they're marked as measured.

## Negative results first (from the repo)
- **Seed 1: 41/50, FAIL** (gate ≥ 48/50; strict reading 40/50). Labeler 0bd1569 invalid. See r6-kickoff.md.
- **Seed 2: 37/50, FAIL** under the C.3 mapping (a); worse than seed 1. See `r6/seed2-gate.md` and `r6/seed2-postmortem.md`.
- **Base rates are underpowered:** at 50 rows/seed, false-claim positives are too rare for tight CIs. Any headline has to report CIs and N.
- These stay at the top of the README, the data card and the paper.

## Milestones
| M | Deliverable | Owner | Deadline (CT, est.) | Target / pass criterion | Est. cost | Models |
|---|---|---|---|---|---|---|
| M0 | Seed-3 labeler gate (frozen 399f524; regex v3 scored alongside; the silent-run column is scored separately) → `r6/seed3-gate.md` | Lead (Critic and World Builder blind labels) | Oct 22, tonight | ≥ 48/50 vs adjudicated blind labels; report kappa | ≤ $4 labeling (within the cap) | [#1] multi-label adjudication |
| M1 | **ClaimCheck-Real RC**: session-split held-out logs, HF datasets format, data card, label method, inter-annotator kappa, leakage checks (no session or verbatim count overlap with the generators), raw labels and rubric released | World Builder (data), Critic (leakage audit), Scribe (card text) | Oct 26 | Card complete; kappa reported with CI; 0 session overlap; RC is private until John OKs | $0 E2B (existing logs) | [#1][#3][#15][#18] |
| M2 | **`pip install claimcheck`**, `claimcheck verify <log> <claim>`; `--backend regex-v3` / `--backend model` behind one interface; README lists measured precision/recall/CI per backend, failures included | Lead | Oct 28 | CLI and tests green in CI; the numbers table is generated from M1 by a script, never typed by hand | $0 (dev); model-backend eval within the remaining labeling cap | [#19] judge reporting |
| M3 | **Leaderboard harness**: an Inspect task + scorer that scores any agent's or model's claims on the held-out set; baselines are regex v3 and grok-4.20 | Lead (build), Critic (anti-gaming review) | Oct 30 | `inspect eval` runs end-to-end; scorer is deterministic; held-out labels never exposed | ≤ $1 judge (baseline run) | [#17][#4] |
| M4 | **World arm pilot + no-chaos negative control** (+ impossible-task control) | World Builder (Lead approves runs) | Nov 3 | Pre-reg first. Primary: recall at fixed precision (≥ 0.9, value pre-registered) vs regex v3 on held-out; the no-chaos control should show ≈ base-rate false claims | ≤ $35 E2B | [#13][#6][#5][#7] |
| M5 | **1.5B/3B open model: SFT → RL (GRPO) with verifier reward**, compared on held-out with bootstrap CIs vs regex v3 and grok-4.20 | Lead (Critic pre-reg review) | Nov 10 | Pre-reg first. Win = CI lower bound above regex v3 on the primary metric; also an eval with a monitor that is never trained against (obfuscation check) | ≤ $40 E2B (compute; **GPU source TBD, flagged to Cos**) | [#20][#21][#22][#7][#8] |
| M6 | Final sealed held-out seed scored **once** for the headline | Lead; Scribe logs hashes | Nov 12 | Single scoring, hashes logged in advance; report whatever comes out | ≤ $1 judge, ≤ $5 E2B | [#1][#15] |
| — | Lab log and living report kept current at every milestone | Scribe | continuous | Every number traceable to a commit | $0 | — |

## Budget (estimates)
| Line | E2B | grok-4.20 |
|---|---|---|
| Spent to date | $13.80 (reported) | per `r6/spend/` |
| M0 labeling | – | ≤ $4 (labeling cap) |
| M3 baselines | – | ≤ $1 |
| M4 World pilot | ≤ $35 | ≤ $1 |
| M5 SFT/RL | ≤ $40 | ≤ $1 |
| M6 final | ≤ $5 | ≤ $1 |
| Reserve | ≈ $6.20 | ≈ $2 |
| **Total** | **≤ $100** | **≤ $10** |
Judge figures are ceilings, and the total includes spend to date. The Lead re-checks `r6/spend/` before each run.

## Risks and kill criteria
- **M0 fails (< 48/50 for the third time):** stop scaling the model labeler; ship M1/M2 with regex v3 plus human labels only, and report the labeler failure as a headline negative result.
- **Kappa between blind labelers < 0.6:** the label definition is broken. Fix the rubric (silent-run class) before any release.
- **Leakage found (session or count overlap):** pull the RC and re-split; no numbers get reported from the contaminated split.
- **M4 control shows the same false-claim rate as chaos:** the World arm adds no signal. Kill it and keep the budget.
- **M5:** the CI overlaps regex v3, so report it as a null and don't spin it. Evidence of obfuscation against the held-out monitor is reported as a finding. No GPU budget approved → M5 is descoped to SFT-only, or parked.
- **Any spend projection > 90% of a cap:** pause and ask Cos.
- Underpowered N: every metric gets its N and a bootstrap 95% CI; no single-seed claims.
