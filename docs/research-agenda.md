# ClaimCheck research agenda: the next 3 rounds after R4

Draft rev 3, 2026-10-22 ~08:45 CT (America/Chicago). Every number comes from the repo `claimcheck-public` (HEAD ab915df)
or from my own offline re-computation, marked as such. **No sandboxes were launched to write this.**

Round naming: R3 = count family (`finetune/count-family/`, pre-reg 5a14571, results 724de33).
"R4" = the rounds now in flight: `realistic-count/` (pre-reg 284cc22) and `scale-family/` (family transfer, pre-reg ab915df).
`world/` has code but no pre-reg yet.

## R3 recap (quoted from README @724de33 and results.json)
Selected-epoch means over 4 seeds: true-claim acc **0.99**, real count catch **0.28** (n=10), held-out format catch/true
**1.00 / 0.96**, wrong-run catch **0.47** (n=15), catch all 0.59, cue-stripped 0.78.
- H1 count ≥0.50: **fail (0.28)**. H2 formats: **pass**. H3 guardrail: **pass (0.99; 0.97–1.00)**. H4 wrong run ≥0.60: **fail (0.47)**.
  H5 cues: pass (catch *rose* 0.59→0.78, which the README calls "not clean"). H6 seed spread on true acc: pass (3 pts).
- Cost: about $2.04 E2B (13,754 sandbox-s).

## R3 corrections (Critic audit `critic/round-3.md`, checked against the repo myself)
1. **H2 is near-trivial. CONFIRMED.** I re-implemented the no-model rule ("supported iff every number in the claim appears
   as a token in the log/command") offline. It scored **77/80 on `test-syn_heldfmt.jsonl`**, the same as the Critic. On
   `test-syn_trainfmt.jsonl` I got **33/40** where the Critic reported 32/40. The difference is probably tokenization and
   doesn't matter here. The JUnit sample shows `tests="17"` verbatim, with the claim "17 tests". So the README line
   "Counting does generalize across synthetic formats" should be withdrawn. H2 measures whether a number is present, not
   whether the model counts.
2. **There are no baselines. CONFIRMED.** All four `out-s*/pred-zeroshot.json` are 0 bytes, from `--skip-zs`. results.json
   has no regex or prior-checkpoint comparison.
3. **The real effect comes from seed 0. CONFIRMED.** Selected epochs and real count catch: s0 ep1 **0.80**, s1 ep3 **0.10**,
   s2 ep2 **0.00**, s3 ep2 **0.20**. `guardrail_met_on_val` is True only for **s2**. Selected-epoch val true acc:
   s0 0.769, s1 0.949, s2 0.974, s3 0.923. Seed 0 collapses to true acc 0.211 / 0.132 at ep2/ep3.
   `out-s3/log.txt` and `out-s3/meta.json` are **0 bytes**, both in the working tree and in commit 724de33.
I did not independently check the Critic's other points (#6 post-hoc analysis code, #7 test-split reuse, #9 the
unablated causal claim). They are plausible from the commit history: `analyze.py` first appears in 724de33, and the
pre-reg says "Same 77-item ... as before".

## R4 (in flight): results placeholder
> **[R4 RESULTS GO HERE]** realistic-count P1/P2/P3 (count ≥0.50, wrong run ≥0.60, true ≥0.95). Family transfer F1/F2/C1
> (family-eval bal-acc ≥0.80 and true ≥0.90; gap to control ≤10 pts; ≥0.50 catch on 30 expanded real count fakes).
> Add the R5 baselines below to these too, if the outputs allow it.

## Hard constraints from the repo (these shape the ranking)
- **Scaling to 1.5B/3B is blocked on E2B CPU.** From the scale-family pre-reg: 1.5B ran out of memory in fp32 at the
  8 GB cap. In bf16 it took 37 s/step and peaked at 7.6 GB, about 12 h/seed. Templates above 8,192 MiB are refused.
- **No new real transcripts exist beyond the 388 already used** (same pre-reg). So a "larger held-out real set" can only
  come from generation, meaning ClaimCheck World, until new agent logs show up.
- The test split has been reused for every round (Critic #7). A fresh split is required anyway.

## Required in R5 and later (non-negotiable)
1. `analyze.py` reports these baselines next to every hypothesis: **zero-shot** (no `--skip-zs`), the **v2 check suite**
   (number-presence regex; frozen, commit hash named in the pre-reg), the **v3 chaos-aware check suite** (below), and a
   **claim-only** baseline.
2. A **held-out-format generator with implicit counts.** The claimed number is never in the log verbatim: sums across
   suites, `x/y` fractions, go-style PASS lines, reruns. The v2 suite must be checked to be near chance on it before training.
3. A **fresh real test split** that no prior round has touched, hashed in the pre-reg commit.
4. **Provenance for every seed:** non-empty `meta.json` and `log.txt`. If either is empty, the seed is invalid and gets rerun (paid from the reserve).
5. `analyze.py` is committed together with the pre-reg, including tie-breaks and metric definitions.

## Negative result to publish now (from the R3 corrections)
**Clean-log counting is solved by a script.** On R3's held-out synthetic formats, a no-model rule ("every number in the
claim appears in the log") scores 77/80, against the model's 1.00 catch / 0.96 true. Clean-format count checking needs no
learned verifier. Any learned-checker claim has to be made on logs where that script fails.

## Spend (see `spend-ledger.md`)
- E2B logged so far: **$7.31** (sandbox logs). The first fine-tune and left-out-recipe rounds are **UNKNOWN** (no sandbox log located).
- Worst case for the 13 open R4 sandboxes: **$8.10** (13 × 4,200 s).
- Cap: **hard $100 E2B** (John via Cos, Oct 22). Remaining budget: **unknown until R4 posts**. Worst case is **$84.59** ($100 − $7.31 − $8.10). With a $10 reserve, the **gate is $74.59**, before the UNKNOWN rounds.
- The reported $8.18 has an unverified source and isn't used.
- xAI API spend (**$6.36**) is outside the cap.
- Rate: $0.0001483/s (≈$0.53 per sandbox-hour), from R3's own $2.04 / 13,754 s. One training run at the 4,200 s cap ≈ **$0.62**.

## Ranked plan

### R5: ClaimCheck World, one locked comparison (rank 1)
- **Why it's frontier:** it's the only way past both binding constraints: no new real logs, and a reused test split.
  Real repos run under real chaos (flaky, skip, timeout, truncate, partial_rerun, wrong_cwd, missing_env;
  `world/world.py`) and get labels from actual reporter output (`world/label.py`). Counts are naturally implicit.
- **The comparison:** World-trained 0.5B checker vs **v2 check suite** vs **v3 chaos-aware check suite** vs **zero-shot**
  vs **claim-only**, at **8 seeds** (0–7).
- **v3 chaos-aware check suite (rule baseline, no model):** flags a claim when
  (a) the log is truncated or the summary line is missing;
  (b) the claim's count doesn't match the **last** rerun;
  (c) skipped/xfail counts make "all N pass" or the total wrong;
  (d) the cwd or test path in the run differs from the claim's.
  It's frozen, and its hash goes in the pre-reg.
- **Core hypothesis (H1):** on held-out repos, the checker's balanced accuracy beats the **best of the v2/v3 suites** by
  ≥15 pts, per claim family and per chaos type. Mean over 8 seeds, true-claim accuracy ≥0.90.
- **Claim-only baseline:** scores the claim text with no log. If it's above chance (bootstrap CI excludes 0.50), labels
  leak through phrasing. That gets flagged, and H1 is reported against it too.
- **Writer shortcut:** claims come from Qwen2.5-0.5B **plus at least one other writer** (a non-Qwen local model, or
  templated + paraphrased claims). Catch is reported **for each writer**. H1 must hold for the non-Qwen writer.
- **Label audit:** hand-check 50 episodes before training. **The set is invalid unless ≥48/50 are correct.** The label
  error rate is reported next to every metric.
- **Repo holdout:** at least **5 repos** held out entirely. Results are reported **per repo**.
- **Real-log transfer (H2):** measured on the **30 expanded real count fakes** with **Wilson 95% CIs**. If it can't be
  run on those 30, H2 is labeled **exploratory**. Not tested on n=10.
- Fix-and-reverify loop: a separate eval (claim → rerun → relabel), with no pass bar.
- **E2B estimate: ≈ $8.1.**
  - Generation: 4 sandboxes × 1 h ≈ $2.1, assuming 10–20 s/episode (unmeasured).
  - Second writer: ≈ $0.5.
  - Training/eval: 8 seeds × 4,200 s ≈ $4.98.
  - Zero-shot: ≈ $0.5.
  - The baselines are offline (free).
  - A one-sandbox smoke test (≈$0.3, included) measures s/episode before the pre-reg locks.
- **Breakthrough:** ≥0.70 catch at true ≥0.95 on held-out repos, ≥20 pts over the best of v2/v3, all 8 seeds within
  15 pts, it holds for every writer, and H2 passes with its Wilson CI. **Nice:** H1 passes but H2 doesn't.
  **Negative worth publishing:** the 0.5B checker can't beat the v3 chaos-aware script.

### R6: RL with a verifier reward vs SFT at 0.5B (rank 2)
- **Why it's frontier:** World provides an executable reward. R3 showed SFT trading recall for the guardrail (seed collapse
  to 0.13–0.21 true accuracy). The question is whether RL removes that trade-off.
- **Three conditions (from the Critic; all are required):**
  1. The reward comes **only from the run-output labels** (`world/label.py` on actual reporter output). It never comes
     from the v3 suite or any rule baseline, which stay evaluation-only.
  2. **Matched compute, items and seeds:** SFT and RL get the same training items, the same per-run wall budget
     (4,200 s force-stop) and **8 seeds each** (0–7).
  3. It **starts only after the R5 label audit passes (≥48/50)**. If the audit fails, R6 doesn't start.
- **Step 0:** a ≈$0.30 feasibility smoke test, to check that an RL (e.g. GRPO) run at 0.5B fits within 4,200 s on the
  8 GB CPU template. If it doesn't fit, publish the bound and stop.
- **Core hypothesis:** on R5's held-out repos, RL matches SFT on true-claim accuracy (≥0.95) and gains ≥15 pts catch, with
  a smaller between-seed spread on catch. Reported against the best of v2/v3, zero-shot and claim-only.
- **E2B ceiling: ≈ $10.3.** Smoke test $0.30, plus 2 arms × 8 seeds × 4,200 s × $0.0001483/s ($4.98 per arm).
- **Breakthrough:** true ≥0.95 *and* catch ≥0.80 across all 8 RL seeds. **Nice:** similar means but more stable. **Negative
  worth publishing:** with exact-execution reward at matched compute, RL is no better than SFT.

### R7: cross-family transfer and a larger held-out set (rank 3)
- **Why it's frontier:** does verification transfer to claim types never trained? This extends R4's family-transfer
  round (F1/F2) to World chaos families.
- **Core hypothesis:** depends on R4's F1 (placeholder). If F1 passes: leave one chaos family out and catch it at ≥0.60,
  true ≥0.90, ahead of the best of v2/v3. If F1 fails: measure how many examples (0/10/50) close the gap.
- **1.5B/3B is not scheduled.** It's infeasible on the 8 GB template (≈12 h/seed, scale-family pre-reg).
- **E2B estimate: ≈ $5–7.** 3–4 leave-one-out arms × 2–4 seeds × $0.62, plus ≈$1 of World generation.
- **Breakthrough:** zero-example held-out-family catch ≥0.70, ahead of v3. **Nice:** transfer with 10 examples.
  **Negative worth publishing:** no family transfer.

## Budget roll-up (worst case, hard $100 E2B cap)
| Item | $ ceiling |
|---|---|
| E2B logged so far | 7.31 |
| 13 open R4 sandboxes at 4,200 s | 8.10 |
| Reserve (reruns of invalid seeds) | 10.00 |
| **Gate for new rounds** | **74.59** |
| R5 World (8 seeds) | 8.1 |
| R6 RL vs SFT (smoke + 2 × 8 seeds) | 10.3 |
| R7 cross-family | 7.0 |
| **Planned R5–R7** | **25.4** (≈49.2 of the gate unallocated) |
This excludes the UNKNOWN first-fine-tune and left-out-recipe rounds. The total is unknown until R4 posts E2B usage.
**Fallback rule (the only one): cut R6 first.**

## Changelog
- rev 2 (08:25 CT): adopted all eight points from the Critic's agenda review (`critic/agenda-review.md`): 8 seeds,
  v2-suite balanced-accuracy bar per family/chaos type, claim-only baseline, second writer, 48/50 label audit, 30 fakes
  with Wilson CIs, ≥5 held-out repos, $5 reserve with R6 cut to a smoke test. Also added the v3 chaos-aware suite, the
  clean-log-counting negative result, the single fallback rule, and a re-costing against `spend-ledger.md`.
  Thanks to the Critic.
- rev 3 (08:45 CT): hard $100 E2B cap with a $10 reserve, so the gate is $74.59. R6 is restored as a full RL-vs-SFT plan under the Critic's three conditions (labels-only reward, matched compute/items/8 seeds, starts only after a 48/50 label audit). Number-presence baseline committed (`baselines/`, 77/80).
