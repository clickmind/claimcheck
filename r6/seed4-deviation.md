# Seed-4 deviation: v2 run #1 crashed; one approved re-launch

## What happened
- v2 run #1 (seed 4) was launched from `labeler/` instead of the repo root. The spend-log path in the frozen code (`r6/spend/labeler-judge-spend.jsonl`) is relative.
- The first API call, for row offset 945, **returned**. `log_call` then raised before the response was parsed or written. **No label was parsed, written to disk or seen by anyone.** (Correction to the Critic's framing: the crash came after the HTTP response came back, but before any model output was parsed or exposed. The response content was discarded in memory.)
- Traceback (from /tmp/v2run.out):
```
  File "/workspace/cc-cap40/labeler/model_labeler_v2.py", line 70, in <module>
    try: res = label_row(r, a.dry_run)
  File "/workspace/cc-cap40/labeler/model_labeler_v2.py", line 53, in label_row
    v1.log_call(rid, usage, "labeler", log); v1.observe(full, usage.get("prompt_tokens", 0))
  File "/workspace/cc-cap40/labeler/model_labeler.py", line 57, in log_call
    with open(log, "a") as f: f.write(json.dumps(rec) + "\n")  # append-only
FileNotFoundError: [Errno 2] No such file or directory: 'r6/spend/labeler-judge-spend.jsonl'
EXIT 1
```
  Line 53 is the `log_call` that runs right after `api(text)` returns. The `parse()` and the output write come later and never ran.

## Unlogged call
- Row 945, grok-4.20, **cost unknown (null)**. Est. under $0.01; unverified. xAI provider usage was not checked: per-request billing data needs the xAI management API/console, not the inference key, so the cost stays null rather than being estimated.
- Placeholder: `r6/spend/labeler-judge-spend-notes.jsonl`. It is not in the main log, because frozen `totals()` sums `r["usd"]` and a null would crash every cap check.

## Partial outputs
- `r6/audits/seed4-model-labels.jsonl` from run #1 had 0 lines. It was deleted before 14fe9e3 and never committed. There are no other partial files.

## Decision
- Lead self-decision, 15:50 CT, 2026-10-22: ONE complete v2 re-launch on all 50 rows, from the repo root, frozen code unchanged. If it crashes again: STOP, with no further attempts.
- Frozen code verified before the re-launch: `labeler/model_labeler_v2.py` 3b26a8e1f93764f93cff4d4cd0d4af7a60d66f012578cc399d3d6dd675578c24, prompt 32bb48b1a2015a533f9e5109f0ccaec6dc84a4dc5af6b0905f8443ef0b6782cc, blind sheet 5a55a27cca114bcb7eec5fd4ed7d69af4b2c4fc4cf9a3a46b3ed1f40cb399157.

## New standing rule
- Labelers and judges always run from the repo root (`cd $(git rev-parse --show-toplevel)`).
