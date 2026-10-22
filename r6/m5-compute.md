# M5 compute options: Qwen2.5-1.5B, SFT then GRPO

Written 2026-10-22 at about 15:40 CT. **$0 spent, no signups, no rentals.** Prices are list prices read from the linked pages today (curl or WebFetch). GPU-hours and dollar totals are **estimates**.

## 1. How round 3 actually ran (from the repo)
- **Count-family run (R3)**, pre-registered in 5a14571, results in 724de33:
  - Model: `Qwen/Qwen2.5-0.5B-Instruct`, LoRA r=16/α=32 on q,k,v,o; fp32; 3 epochs; 400 train examples; maxlen 768. Source: `finetune/count-family/out-s0/meta.json`.
  - Hardware: **CPU-only E2B sandbox** (template `claimcheck-ml`, 8 vCPU / 8 GB per README §"Model"), driven by `finetune/count-family/run_e2b3.py` (1 h sandbox timeout, kept alive with `set_timeout`).
  - Wall time: 3,443 s for seed 0 (train plus eval), from `out-s0/meta.json` and `log.txt`. 4 seeds took 2,857–3,739 s each (`finetune/count-family/my-sandboxes.txt`).
  - Cost: **about $2.04 of E2B CPU time** for 4 sandboxes and 13,754 sandbox-seconds (README).
- Earlier 0.5B run: training took about 15 minutes on the same sandbox type (README). Old stash `stash@{0}` (read with `git show`, not popped): `finetune/run-q05.txt` ends with "done 872" s; `finetune/run-q15.txt` (the 1.5B attempt) was still at "zeroshot done 278" after 1,385 s.
- README: "**1.5B not finished.** … on CPU, it would not have finished inside the sandbox time limit."
- **Can this path be reused?** **No for M5.** E2B is CPU-only (see §2). A 1.5B model on CPU already failed under the Hobby plan's 1 h session limit, and GRPO adds many generation rollouts per step, which makes CPU much worse. The scripts (`train3.py`, `run_e2b3.py` with sandbox logging and guaranteed kill) can be ported to a GPU host almost unchanged.

## 2. Does E2B have GPUs?
**No.** https://e2b.dev/pricing: "Sandboxes are CPU-only; E2B does not offer GPU sandboxes." Limits: 1–8 vCPU and 1–8 GiB RAM, at $0.000014/vCPU-s and $0.0000045/GiB-s. The Hobby plan caps sessions at 1 h; Pro is $150/mo for 24 h. Enterprise is the only route to "more powerful compute", with a $3,000/mo minimum. **This means M5 GPU spend can't come from the E2B cap; Cos/John need to approve a separate GPU line.**

## 3. GPU rental prices (on-demand, per GPU-hour, read today)
| Provider | GPU | Price | Source |
|---|---|---|---|
| Modal | A100 80GB | $0.000694/s = **$2.50/h** | https://modal.com/pricing |
| Modal | L40S 48GB | $0.000542/s = $1.95/h | same |
| Modal | H100 | $0.001097/s = $3.95/h | same |
| RunPod | A100 SXM 80GB | Community $1.39/h, **Secure $1.79/h** | https://www.runpod.io/pricing |
| RunPod | L40S | Community $0.79/h, Secure $1.09/h | same |
| Lambda | A100 40GB (1x) | **$1.99/h** (+ tax) | https://lambda.ai/pricing |
| Lambda | H100 PCIe (1x) | $3.29/h | same |

Caveats from the pages:
- Modal: the Starter plan is $0 with **$30/month of included compute**. Per-second billing applies to Functions; Sandboxes are 3x, and so are non-preemptible jobs. Region pinning costs 1.15–1.75x.
- RunPod: "Community" capacity is less reliable than "Secure".
- Lambda: instances are billed hourly and must be shut down by hand.

## 4. Cost estimates for a 1.5B model, a few thousand examples (ESTIMATES)
Assumptions (not measured; there are no published timings for this exact setup, so treat these as order-of-magnitude):
- **SFT:** about 3k examples × ≤768 tokens × 3 epochs ≈ 7M tokens; LoRA or full fine-tune of 1.5B in bf16 on one 40–80 GB GPU. **Estimate 1 GPU-h** including model download and eval. Method: TRL SFTTrainer, https://huggingface.co/docs/trl/main/en/sft_trainer
- **GRPO:** about 1k prompts × 8 generations, 1 epoch, short one-word/JSON completions, reward from our verifier (regex v3 / label match), vLLM generation. **Estimate 4–8 GPU-h.** Method: TRL GRPOTrainer, https://huggingface.co/docs/trl/main/en/grpo_trainer; the recipe follows DeepSeek-R1 (https://arxiv.org/abs/2501.12948) and Tulu 3 RLVR (https://arxiv.org/abs/2411.15124).
- **2x debug/rerun factor** on top (shown as the high end). Seeds beyond 1 multiply the cost.

| Option | $/GPU-h | SFT (1–2 h) | SFT+GRPO (5–9 h → ×2 = 10–18 h) |
|---|---|---|---|
| Modal A100 80GB | 2.50 | $2.50–5.00 | $12.50–45.00 |
| RunPod A100 SXM (Secure) | 1.79 | $1.79–3.58 | $8.95–32.22 |
| Lambda A100 40GB | 1.99 | $1.99–3.98 | $9.95–35.82 |
| Modal L40S (cheaper; 48 GB is fine for 1.5B) | 1.95 | $1.95–3.90 | $9.75–35.10 |

The low end is 5 h with no rerun; the high end is 9 h × 2.

## 5. Recommendation
**Modal, A100 80GB (or L40S to save money), run as Functions, not Sandboxes.**
- Per-second billing, so there's no idle-instance risk.
- Serverless Python, which is close to our `run_e2b3.py` pattern.
- The $30/month included compute on the free Starter plan likely covers SFT plus one GRPO pilot, an estimated $12.50–22.50 before reruns.
- 80 GB fits vLLM plus training for 1.5B on one GPU.

RunPod Secure is about 30% cheaper per hour but bills a running pod even while it sits idle. It's the fallback if Modal doesn't suit.

**Needs John/Cos before anything happens:** a Modal account signup (John's sign-in) and a GPU budget line separate from the E2B $100 cap. Proposal: ≤ $40 GPU for M5 with a kill switch at $30, plus a pre-registration before the first run.
