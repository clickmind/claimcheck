# Pre-registration: frontier-judge baselines (run #1)
Written and committed **before any API call**. 2026-10-22 ~09:15 CT. Approved by John Golat, 09:05 CT. Hard model-API cap $55. E2B $0.

## Models (exact IDs, xAI API https://api.x.ai/v1, chat/completions)
- `grok-4.20-0309-non-reasoning` (list $1.25 / $2.50 per 1M in/out, <200k prompt; https://docs.x.ai/docs/models, read 09:00 CT)
- `grok-4.7` (list $2.00 / $6.00; same page). Reasoning tokens are billed as output.
- **GPT and Claude: SKIPPED.** No `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` exists in the environment. That is a deviation from the plan, recorded here before any run.

## Prompt (fixed)
Identical to `src/score.ts` prompt v1.1 (the `V !== "1"` branch) at the data commit. Synthetic items without a `claim` field use `checked_span` as the full sentence. The prompt is reproduced in `judges/run_judges.py`. The answer is parsed as: the first occurrence of "unsupported" means unsupported, "supported" means supported, and anything else is counted as unparsed, scored **wrong**.

## Item sets (data pinned at origin/main **8079320**)
| Set | File | n |
|---|---|---|
| real77 | `data/claims.jsonl` ∩ `finetune/split.json` split=test | 77 (38 supported, 39 not) |
| masked77 | `finetune/realistic-count/test-masked.jsonl` | 77 |
| heldout80 | `finetune/realistic-count/test-syn_heldfmt.jsonl` | 80 |
| trainfmt33 | `finetune/realistic-count/test-syn_trainfmt.jsonl` | 33 |
| family41 | `finetune/scale-family/test-family.jsonl` | 41 |
| xcount30 | `finetune/scale-family/test-xcount.jsonl` | 30 (all false, so catch only) |
Gold labels: `supported` is true, and `unsupported` / `overclaimed` are false.

## Calls
Each item gets 1 primary call at temperature 0, plus 8 repeats at temperature 0.7 with `seed` = 1..8 (sent; recorded if the API ignores it). That's 9 calls per item and 338 items, so 3,042 calls per model. grok-4.20 runs first, then grok-4.7.

## Metrics (primary = the temperature-0 call)
- Balanced accuracy = mean of true-claim accuracy and false-claim catch, with **Wilson 95% CIs** on each component. The balanced-accuracy CI is a bootstrap over items (2,000 resamples, seed 0).
- **Miss rate on false claims** = 1 − catch, with a Wilson CI.
- **Per-repeat spread:** min, max and SD of balanced accuracy across the 8 repeats, plus per-item majority-vote agreement.

## Comparators (offline, no model)
- Rules v1 (`results/rules.json` @1852c8e: 0.974 accuracy on real77, per README).
- v2/v3/v3.1 check suites (`baselines/checks/*` @aea8be2 on origin/baselines), where they run on these files.
- Number-presence (`baselines/number_presence.py`).
- Qwen2.5-0.5B+LoRA: 0.831 on real77 (README).

## Stop rule
A live tracker computes spend = usage tokens × the list prices above. **All calls stop if the projected spend after the next call would exceed $53** (hard cap $55). Partial results are reported as partial.

## Addendum A: Claude arm (written and committed before any Claude call, 2026-10-22 ~09:52 CT)
- Model `claude-sonnet-5-5` (Anthropic Messages API, `https://api.anthropic.com/v1/messages`). List price $2 / $10 per 1M in/out, cache reads $0.10 (https://docs.anthropic.com/en/docs/about-claude/pricing, read 09:40 CT). The ID was verified via the models list.
- Same prompt, same 338 items, same parse rule and metrics as above. 1 call at temperature 0 plus 8 repeats at temperature 0.7, with `max_tokens` 2048. Anthropic has no `seed` parameter, so repeats differ only by sampling.
- Thinking is adaptive and can't be disabled on Sonnet 5.5, so the defaults are used. If the API rejects a temperature with thinking on, that gets recorded as a deviation and the API default is used.
- The stop rule is unchanged. Calls stop if the cumulative projected model-API total (including $12.14 already spent on Grok) would exceed $53. Cost is computed from returned usage × list price (input, cache write 1.25×, cache read $0.10, output).
- Opus is not run (its projected ~$36 would break the stop).
