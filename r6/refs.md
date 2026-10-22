# r6 reference set: what ClaimCheck models from the best existing work

Checked 2026-10-22 at about 15:25 CT. "200" means curl returned HTTP 200. "WebFetch" means curl got a 403 from bot blocking, but the page was fetched and read through WebFetch. arXiv titles were checked against the abstract page.

| # | Reference | Link | Status | What we model from it |
|---|---|---|---|---|
| 1 | SWE-bench Verified (OpenAI, Aug 2024) | https://openai.com/index/introducing-swe-bench-verified/ | WebFetch OK (read in full) | **Curation and adjudication.** 93 developers took onboarding tests built from 50 gold samples; every sample was labeled 3x; the 0–3 severity rubric is ensembled by taking the max, and any severe flag drops the sample (68.3% were filtered out); annotations and rubric were released. Our M1: we use a gold onboarding set, multi-labeler, conservative ensembling, and release the raw labels and rubric. |
| 2 | SWE-bench (Jimenez et al.) | https://arxiv.org/abs/2310.06770 | 200, title checked | FAIL_TO_PASS / PASS_TO_PASS: grounding labels in execution. Our labels come from the actual run output. |
| 3 | SWE-bench Verified dataset (HF) | https://huggingface.co/datasets/princeton-nlp/SWE-bench_Verified | 200 | Release format for M1. |
| 4 | SWE-bench site / leaderboard | https://www.swebench.com/ | 200 | Leaderboard and harness pattern for M3. |
| 5 | METR, "Recent Frontier Models Are Reward Hacking" | https://metr.org/blog/2025-06-05-recent-reward-hacking/ | 200, title checked | Taxonomy of reward hacks in agentic tasks; the false claims of success that we detect. |
| 6 | METR public task suite | https://github.com/METR/public-tasks | 200 | Task-family packaging and standardized task format for the World arm (M4). |
| 7 | OpenAI, "Detecting misbehavior in frontier reasoning models" (Mar 2025) | https://openai.com/index/chain-of-thought-monitoring/ | WebFetch OK (read in full) | Real cases of test subversion (conftest skip, `verify` returns true). Action monitor vs CoT monitor. Optimization pressure on a monitor teaches the model to hide intent → **M5 risk: RL against our verifier can teach evasion; we must hold out a monitor that is never trained against.** |
| 8 | Baker et al., Monitoring Reasoning Models for Misbehavior… | https://arxiv.org/abs/2503.11926 | 200, title checked | Paper version of #7; obfuscation under pressure. |
| 9 | Anthropic, Sabotage evaluations | https://www.anthropic.com/research/sabotage-evaluations | 200 | Design for evals of sandbagging and undermining oversight. |
| 10 | Benton et al., Sabotage Evaluations for Frontier Models | https://arxiv.org/abs/2410.21514 | 200, title checked | Paper for #9; how to set thresholds and controls. |
| 11 | Claude 4 system card (Anthropic) | https://www.anthropic.com/claude-4-system-card | 200; page text contains a "Reward hacking" heading | Reports that frontier models special-case tests and claim success; motivates the claim-vs-evidence check. Section contents not re-read in detail (**partially verified**). |
| 12 | van der Weij et al., AI Sandbagging | https://arxiv.org/abs/2406.07358 | 200, title checked | Strategic underperformance; a negative-control design. |
| 13 | ImpossibleBench | https://arxiv.org/abs/2510.20270 | 200, title checked ("Measuring LLMs' Propensity of Exploiting Test Cases") | Impossible-by-construction tasks: any "pass" is a cheat. This gives a **ground-truth negative control** for M4 (the no-chaos control and an impossible-task arm). |
| 14 | TruthfulQA | https://arxiv.org/abs/2109.07958 | 200 | Adversarial item design and the truthful-vs-informative split. Our analogue: separate claim precision from abstention. |
| 15 | SimpleQA (paper) | https://arxiv.org/abs/2411.04368 | 200, title checked ("Measuring short-form factuality…") | Single indisputable answer, created and checked by two independent annotators, scored as correct/incorrect/not attempted. Our label space includes "silent/unsupported" as its own class (see the Critic's seed-3 note). |
| 16 | SimpleQA (OpenAI page) | https://openai.com/index/introducing-simpleqa/ | **NOT verified** (curl 403; not fetched) | Same as #15; cite the arXiv version. |
| 17 | UK AISI Inspect docs | https://inspect.aisi.org.uk/ | 200, title "Inspect" | Task/solver/scorer format for the M3 leaderboard harness. |
| 18 | HF dataset cards guide | https://huggingface.co/docs/hub/datasets-cards | 200 | Data card fields for M1. |
| 19 | Zheng et al., Judging LLM-as-a-judge (MT-Bench) | https://arxiv.org/abs/2306.05685 | 200 | Judge biases (position, verbosity, self-preference) and judge–human agreement. Reporting for our grok-4.20 labeler. |
| 20 | DeepSeek-R1 | https://arxiv.org/abs/2501.12948 | 200, title checked | RL with rule-based verifiable rewards (GRPO) after a cold-start SFT, for M5. |
| 21 | Tulu 3 (RLVR) | https://arxiv.org/abs/2411.15124 | 200 | SFT → preference → RL with verifiable rewards; recipe and decontamination practice for M5. |
| 22 | TRL GRPOTrainer docs | https://huggingface.co/docs/trl/main/en/grpo_trainer | 200 | Implementation for the M5 RL step. |

Couldn't verify: #16 (use #15 instead). #11 is only partly verified (the heading exists; section details were not re-read).
