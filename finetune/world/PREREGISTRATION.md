# Pre-registration: ClaimCheck World (pre-registration only; NOT run in this round)

Written 2026-10-22 (America/Chicago), before any World data was generated or any model trained on it. Per the
research lead, runs are handed to the team that owns R5. Only a 12 s environment probe and one aborted 6-episode smoke
test ran (sandbox ids in `my-sandboxes.txt`). The smoke produced no data that was used.

## Idea
Unit tests check what the author thought of. Real agent runs fail in messier ways. Instead of templating fake claims,
**run real tiny repos in E2B and break them**, then let a real model write the claim and label it from what actually
happened.

## Environment (`world.py`, `label.py`, `gen_e2b.py`)
- Each episode builds a fresh tiny repo: **vitest** (Node 20) or **pytest**, with 1–4 test files and 2–15 tests each.
- **Chaos**, 0–2 per episode, sampled from: flaky tests (real `Math.random` / `random`), a skipped test file, a
  timeout (slow test plus `timeout 5`, exit 124, partial output), a truncated log shown to the agent, a partial rerun of
  one file, the wrong working directory (no tests found), and a missing env var (`API_BASE`) that a test needs.
- **Claim writer:** Qwen2.5-0.5B-Instruct, run locally (no paid API), reads exactly the logs the agent saw and returns
  JSON `{status, passed, total}`. That is rendered into agent-style claim text.
- **Ground truth:** the vitest JSON reporter / pytest JUnit XML from the same run, not the displayed log. A claim is
  *supported* only if some logged run exited 0 with 0 failures and the claimed passed count (and total, if stated)
  matches that run. Non-success claims are dropped. No hand-labeling.
- Episodes are split into world-train / world-val / world-test by episode, so each repo instance is in one split only.

## Arms (Qwen2.5-0.5B, same LoRA / lr / 3 epochs / 400 balanced items / selection rule as `../realistic-count`)
- **Synthetic (baseline):** the `../realistic-count` training set as pre-registered (generator pairs).
- **World:** identical, except the synthetic generator pairs (`rsyn:*`, `syn:*`) are replaced, item for item, by
  World episodes balanced 50/50 supported / unsupported.
- 4 seeds each. Real agent logs stay held out **by session** (`../split.json`, test split of `data/claims.jsonl`).

## Hypotheses and pass thresholds (selected epoch, mean over 4 seeds)
- **W-a:** World beats Synthetic on held-out real logs. It passes if the World arm has **higher real count catch** (expanded 30-item
  set from `../scale-family`) **and higher real wrong-run catch** (n=15) than Synthetic, with both arms at real
  true-claim accuracy **≥ 0.95**. A difference smaller than 10 points on either counts as no difference (fail).
- **W-b, fix loop:** on world-test episodes, the checker (World arm, selected epoch) scores each initial claim. Flagged
  claims go back to the same claim writer with "a reviewer says this claim is not supported by the logs; re-read and
  correct it", and the corrected claim is re-labeled from ground truth. It passes if the share of episodes that end with a
  true claim rises by **≥ 10 points** over the initial share, with a 95% episode-bootstrap CI excluding 0. Also reported:
  the same loop with *every* claim sent back (no checker), to separate the checker's value from just asking twice.

## Budget
Must fit inside the series' $40 cap. Estimated cost is about $2 for generation (4 sandboxes × about 150 episodes) plus about $4.5 for 8 training runs.
