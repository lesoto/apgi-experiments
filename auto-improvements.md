# Auto-Improvement Folder — Comprehensive Audit Report

**Date**: 2026-03-22
**Scope**: Full static and dynamic analysis of `auto-improvement/` directory
**Files audited**: `prepare.py`, `train.py`, `pyproject.toml`, `README.md`, `USAGE.md`, `iowa.md`

---

## Executive Summary

The `auto-improvement/` folder is an adapted copy of [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) project — an autonomous AI research loop where an agent iteratively modifies `train.py`, trains a small GPT model for 5 minutes, evaluates, and keeps/discards changes. It also contains documentation (`iowa.md`, `USAGE.md`) for adapting this system to Iowa Gambling Task (IGT) psychological experiments.

**Overall Rating: 38/100**

The code itself (`prepare.py`, `train.py`) is well-written ML infrastructure, but the integration into this repository has **critical bugs**, **missing files**, **documentation inconsistencies**, and **architectural gaps** that would prevent it from functioning as intended.

---

## 1. Critical Bugs (Severity: Blocker)

### BUG-1: Broken Forward Pass in GPT Model — `train.py:418-421`

```python
for i, block in enumerate(self.transformer.h):
    x = self.resid_lambdas[i] * x + self.x0_lambdas[i] * x0
ve = self.value_embeds[str(i)](idx) if str(i) in self.value_embeds else None
x = block(x, ve, cos_sin, self.window_sizes[i])
```

**Problem**: The `ve` computation and `block()` call are **outside the for-loop** due to incorrect indentation. Only the residual lambda scaling runs inside the loop; the actual attention+MLP computation runs once with only the last layer's block. This means **all transformer layers except the last are completely bypassed** — the model is effectively a 1-layer transformer pretending to be an N-layer one.

**Expected (correct) code:**
```python
for i, block in enumerate(self.transformer.h):
    x = self.resid_lambdas[i] * x + self.x0_lambdas[i] * x0
    ve = self.value_embeds[str(i)](idx) if str(i) in self.value_embeds else None
    x = block(x, ve, cos_sin, self.window_sizes[i])
```

**Impact**: The model will train and produce a `val_bpb` score, but it will be drastically worse than expected because only 1 of 8 layers is actually computing attention. This bug silently degrades quality without causing a crash, making it especially dangerous in an autonomous loop where the agent may waste hundreds of experiments trying to optimize a fundamentally broken model.

---

### BUG-2: Missing `run_igt.py` — Referenced But Does Not Exist

`iowa.md` and `USAGE.md` both reference `run_igt.py` as the primary file the agent modifies for IGT experiments:

> *"Modify `run_igt.py` — This is the only file you edit."* — iowa.md:30

```bash
$ ls auto-improvement/
README.md  USAGE.md  iowa.md  prepare.py  pyproject.toml  train.py
```

**No `run_igt.py` exists.** The entire IGT adaptation documented in `iowa.md` and `USAGE.md` is non-functional. An agent following these instructions would fail immediately.

---

### BUG-3: Unused/Dead Variable — `train.py:630`

```python
HDEVICE_BATCH_SIZE = 16  # Further reduced for MPS/CPU memory constraints
```

This variable is defined but **never used anywhere**. It appears to be a typo/leftover from `DEVICE_BATCH_SIZE`. The actual `DEVICE_BATCH_SIZE` is set dynamically at lines 67-70 based on device type, and the hyperparameter block value at line 630 is shadowed by the earlier assignment. This dead variable is confusing.

---

### BUG-4: `torch.compile` Disabled Without Conditional Logic — `train.py:717`

```python
# model = torch.compile(model, dynamic=False)  # Disabled for MPS/CPU
```

The comment says "Disabled for MPS/CPU" but it's disabled for **all platforms including CUDA**. On CUDA (the primary target), `torch.compile` provides significant speedups (often 20-40%). This should be conditionally enabled:

```python
if device.type == "cuda":
    model = torch.compile(model, dynamic=False)
```

---

## 2. High-Severity Issues

### ISSUE-1: Redundant Flash Attention Initialization — `train.py:42-44, 63-64`

```python
# Line 42-44 (inside if cuda block):
    try:
        fa3 = get_kernel(repo).flash_attn_interface
        use_flash_attn = True

# Line 63-64 (after all device blocks):
if use_flash_attn:
    fa3 = get_kernel(repo).flash_attn_interface  # REDUNDANT
```

`fa3` is loaded twice when `use_flash_attn` is True. The second load at line 63-64 is redundant and wastes startup time. It should be removed.

---

### ISSUE-2: `pickle.load` for Tokenizer Is a Security Risk — `prepare.py:241-242`

```python
@classmethod
def from_directory(cls, tokenizer_dir=TOKENIZER_DIR):
    with open(os.path.join(tokenizer_dir, "tokenizer.pkl"), "rb") as f:
        enc = pickle.load(f)
```

`pickle.load()` executes arbitrary Python code. If the cache directory is tampered with (e.g., a compromised download, shared filesystem), this is a remote code execution vector. In an autonomous agent loop where the agent downloads data from the internet and operates unattended, this is a meaningful risk.

**Mitigation**: Use `pickle.load()` with restricted unpickler, or switch to a safer serialization format (JSON for the mergeable ranks, or `safetensors`).

---

### ISSUE-3: `torch.load` Without `weights_only=True` — `prepare.py:278`

```python
def get_token_bytes(device="cpu"):
    path = os.path.join(TOKENIZER_DIR, "token_bytes.pt")
    with open(path, "rb") as f:
        return torch.load(f, map_location=device)
```

Since PyTorch 2.6+, `torch.load` without `weights_only=True` triggers a `FutureWarning` and will eventually default to safe-only loading. This should be:

```python
return torch.load(f, map_location=device, weights_only=True)
```

---

### ISSUE-4: No Graceful Error on Missing Tokenizer — `train.py:658`

```python
tokenizer = Tokenizer.from_directory()
```

If `prepare.py` hasn't been run first, this will throw a raw `FileNotFoundError` with no helpful message. Should catch and print:
```
Error: Tokenizer not found. Run `uv run prepare.py` first.
```

---

### ISSUE-5: Device Comparison Using String — `train.py:248`

```python
if str(device) == "cuda":
    cos, sin = cos.bfloat16(), sin.bfloat16()
```

Inside `_precompute_rotary_embeddings`, the device is a `torch.device` passed in or inferred. Comparing `str(device) == "cuda"` is fragile — it would fail for `"cuda:0"` or `"cuda:1"`. Use:

```python
if device is not None and torch.device(device).type == "cuda":
```

---

## 3. Medium-Severity Issues

### ISSUE-6: Documentation Inconsistency — `USAGE.md` vs `iowa.md`

Both files contain nearly identical content copy-pasted from the autoresearch README, but with contradictions:

| Topic | USAGE.md | iowa.md |
|---|---|---|
| Agent instruction file | `program.md` (line 15) | `program.md` (line 15) |
| IGT instruction file | `iowa.md` (line 97) | — |
| References `run_igt.py` | Yes (line 125) | Yes (line 30) |
| Time budget | "5 minutes" (line 17) AND "10 minutes" (line 99) | "10 minutes" (line 49) |

The files contradict each other on time budgets and reference files that don't exist (`program.md`, `run_igt.py`). Neither `program.md` nor `EXPERIMENT.md` (referenced in USAGE.md:89) exist in the folder.

---

### ISSUE-7: `prepare.py` Constants Don't Match IGT Domain

`prepare.py` defines LLM training constants:
```python
MAX_SEQ_LEN = 2048  # context length
TIME_BUDGET = 300   # training time budget in seconds (5 minutes)
EVAL_TOKENS = 40 * 524288  # number of tokens for val eval
```

But `iowa.md` describes IGT experiments with "10 minutes per experiment" and "deck configurations." The `prepare.py` has zero IGT-related code — no deck definitions, no net score calculation, no trial logic. The IGT adaptation described in the documentation is entirely aspirational with no implementation.

---

### ISSUE-8: MPS/CPU Fallback Is Incomplete — `train.py:46-61`

The MPS/CPU device paths have several issues:
- `H100_BF16_PEAK_FLOPS` is set to placeholder values (`1e12` for MPS, `1e10` for CPU), making MFU reporting meaningless
- Variable is still named `H100_BF16_PEAK_FLOPS` even on non-H100 devices
- `torch.amp.autocast(device_type="mps", dtype=torch.float32)` is a no-op (autocast to float32 on MPS doesn't do anything useful)
- The `DEVICE_BATCH_SIZE` for MPS/CPU (16) combined with `MAX_SEQ_LEN` (2048) means 32K tokens per micro-batch, which may OOM on many consumer GPUs/Mac

---

### ISSUE-9: Assertion Will Fail on Certain Batch Sizes — `train.py:705`

```python
assert TOTAL_BATCH_SIZE % tokens_per_fwdbwd == 0
```

With `DEVICE_BATCH_SIZE=16` and `MAX_SEQ_LEN=2048`, `tokens_per_fwdbwd = 32768`. `TOTAL_BATCH_SIZE = 2**17 = 131072`. `131072 / 32768 = 4` — this works. But if someone changes `DEVICE_BATCH_SIZE` to, say, 24, the assertion fails with an unhelpful error. Should use a clear error message.

---

### ISSUE-10: `weight_decay` Applied Asymmetrically — `train.py:514-516`

```python
mask = (g * stacked_params) >= 0
stacked_params.sub_(lr * g + lr * wd * stacked_params * mask)
```

Cautious weight decay is only applied to Muon parameters where the gradient aligns with the parameter direction. For AdamW parameters, `weight_decay` is hardcoded to `0.0` for all groups (lines 350, 356, 362, 368, 374). This means only Muon-optimized matrix parameters get weight decay. This may be intentional but is not documented.

---

## 4. Low-Severity Issues

### ISSUE-11: No `.gitignore` in `auto-improvement/`

The folder lacks a `.gitignore`. Running the system would generate:
- `run.log`
- `results.tsv`
- `__pycache__/`
- `~/.cache/autoresearch/` (external, but worth noting)

These should be explicitly ignored.

---

### ISSUE-12: Hardcoded Dataset URL May Break — `prepare.py:41-43`

```python
BASE_URL = (
    "https://huggingface.co/datasets/karpathy/climbix-400b-shuffle/resolve/main"
)
```

The URL references a specific HuggingFace dataset. If the dataset is renamed, made private, or removed, all downloads will fail silently (after 5 retries). There's no checksum verification on downloaded files — a corrupt download would persist as a valid-looking `.parquet` file.

---

### ISSUE-13: GC Freeze May Cause Memory Issues — `train.py:819-822`

```python
if step == 0:
    gc.collect()
    gc.freeze()
    gc.disable()
```

Disabling Python GC and freezing all current objects prevents GC pause stalls but means any circular references created after step 0 will never be collected. In long-running training (300s), this could leak memory. The periodic `gc.collect()` every 5000 steps (line 823-824) partially mitigates this but doesn't unfreeze objects.

---

### ISSUE-14: `USAGE.md` Is a Near-Duplicate of `README.md`

The first ~81 lines of `USAGE.md` are almost verbatim copies of `README.md`. Only lines 82-325 add new content (IGT adaptation). This duplication will lead to drift — any update to one file would need to be mirrored.

---

### ISSUE-15: No Type Annotations

Neither `prepare.py` nor `train.py` use type annotations on any function signature. For a codebase intended to be modified by AI agents, type annotations would significantly improve the agent's ability to understand parameter types and return values.

---

## 5. Architecture Assessment

### 5.1 Design Strengths

- **Clear separation of concerns**: `prepare.py` (fixed infrastructure) vs `train.py` (modifiable experiment code) is a clean boundary
- **Deterministic evaluation**: Fixed `evaluate_bpb` function with pinned validation shard ensures fair comparison
- **Robust download logic**: Retry with exponential backoff, temp file + atomic rename pattern
- **Efficient dataloader**: Best-fit packing with 100% utilization, pre-allocated pinned buffers, async GPU transfer
- **Modern optimizer**: MuonAdamW with polar express orthogonalization, NorMuon variance reduction, and cautious weight decay

### 5.2 Design Weaknesses

- **No isolation between experiments**: The autonomous loop modifies `train.py` in-place and relies on `git reset --hard` for rollback. If the agent introduces a syntax error, the loop breaks. There's no sandbox or validation step before execution.
- **No experiment registry**: Results are logged to a flat TSV file with no structured metadata. There's no way to associate a result with the exact code diff that produced it.
- **Single-file constraint is fragile**: All model code, optimizer code, hyperparameters, and training loop are in one 869-line file. A change to the optimizer can accidentally break model initialization.
- **No checkpointing**: If training crashes at minute 4:59, all 5 minutes of work are lost. There's no periodic checkpoint saving.
- **No sample generation**: The system trains models but never generates text samples, making it impossible to qualitatively evaluate what the model learned.

### 5.3 Dependency Analysis

| Dependency | Version | Purpose | Risk |
|---|---|---|---|
| `torch` | ==2.9.1 | Core ML framework | Pinned — good for reproducibility, risky for security patches |
| `kernels` | >=0.11.7 | Flash Attention 3 kernel loading | Niche package, may break |
| `rustbpe` | >=0.1.0 | BPE tokenizer training | Rust extension, platform-specific |
| `tiktoken` | >=0.11.0 | Tokenizer encoding/decoding | Stable, OpenAI-maintained |
| `pyarrow` | >=21.0.0 | Parquet file I/O | Stable |
| `requests` | >=2.32.0 | HTTP downloads | Stable |
| `numpy` | >=2.2.6 | Not directly imported | Transitive dependency |
| `pandas` | >=2.3.3 | Not directly imported | Unnecessary — should be removed |
| `matplotlib` | >=3.10.8 | Not directly imported | Unnecessary — should be removed |

**Unused dependencies**: `pandas` and `matplotlib` are listed in `pyproject.toml` but never imported in `prepare.py` or `train.py`. They add ~100MB of install weight for no benefit.

---

## 6. IGT Adaptation Assessment

The `iowa.md` and `USAGE.md` documents describe adapting the autoresearch loop for Iowa Gambling Task experiments. This adaptation is **0% implemented**:

| Component | Status |
|---|---|
| `run_igt.py` (core experiment file) | Missing |
| `program.md` / `EXPERIMENT.md` | Missing |
| IGT deck configurations in `prepare.py` | Missing |
| Net score evaluation metric | Missing |
| Data directory `data/stimuli/` | Missing |
| Results tracking (`results.tsv`) | No template |

The documentation reads as a design document, not a usage guide. It should be clearly labeled as "Planned" or "Design Spec" rather than presented as functional instructions.

---

## 7. Roadmap to 100/100

### Priority 1 — Fix Critical Bugs (Impact: +25 points)

| # | Action | File | Effort |
|---|---|---|---|
| 1 | **Fix forward pass indentation** — indent `ve` and `block()` lines into the for-loop | `train.py:420-421` | 5 min |
| 2 | **Create `run_igt.py`** or remove all IGT references | New file or `iowa.md`/`USAGE.md` | 2-4 hours |
| 3 | **Remove dead `HDEVICE_BATCH_SIZE`** variable | `train.py:630` | 1 min |
| 4 | **Conditionally enable `torch.compile`** for CUDA | `train.py:717` | 5 min |

### Priority 2 — Fix Security & Safety Issues (Impact: +15 points)

| # | Action | File | Effort |
|---|---|---|---|
| 5 | Add `weights_only=True` to `torch.load` | `prepare.py:278` | 1 min |
| 6 | Add restricted unpickler or switch tokenizer format | `prepare.py:241` | 1 hour |
| 7 | Add download checksum verification | `prepare.py:63-94` | 30 min |
| 8 | Fix device string comparison | `train.py:248` | 5 min |

### Priority 3 — Fix Documentation (Impact: +10 points)

| # | Action | File | Effort |
|---|---|---|---|
| 9 | Deduplicate `USAGE.md` — remove copy-pasted README content | `USAGE.md` | 30 min |
| 10 | Mark IGT adaptation as "Design Spec / Not Yet Implemented" | `iowa.md`, `USAGE.md` | 10 min |
| 11 | Fix time budget inconsistency (5 min vs 10 min) | `USAGE.md:17,99` | 5 min |
| 12 | Create `program.md` or remove references to it | New file or docs | 30 min |

### Priority 4 — Remove Redundancy (Impact: +5 points)

| # | Action | File | Effort |
|---|---|---|---|
| 13 | Remove redundant `fa3` re-initialization | `train.py:63-64` | 1 min |
| 14 | Remove unused `pandas` and `matplotlib` from deps | `pyproject.toml` | 1 min |
| 15 | Rename `H100_BF16_PEAK_FLOPS` to `DEVICE_PEAK_FLOPS` for non-H100 | `train.py` | 5 min |

### Priority 5 — Add Missing Infrastructure (Impact: +15 points)

| # | Action | File | Effort |
|---|---|---|---|
| 16 | Add `.gitignore` for `auto-improvement/` | `.gitignore` | 5 min |
| 17 | Add graceful error on missing tokenizer | `train.py:658` | 10 min |
| 18 | Add type annotations to public functions | Both `.py` files | 2 hours |
| 19 | Add model checkpointing (periodic save) | `train.py` | 1 hour |
| 20 | Add text sample generation after training | `train.py` | 30 min |

### Priority 6 — Robustness & Testing (Impact: +15 points)

| # | Action | File | Effort |
|---|---|---|---|
| 21 | Add unit tests for `Tokenizer`, `make_dataloader`, `evaluate_bpb` | New test file | 3 hours |
| 22 | Add syntax validation step before running experiments | Agent loop | 1 hour |
| 23 | Add `--dry-run` flag to `train.py` for testing without GPU | `train.py` | 1 hour |
| 24 | Add experiment isolation (copy `train.py` before modification) | Agent loop | 1 hour |

### Priority 7 — Polish (Impact: +15 points)

| # | Action | File | Effort |
|---|---|---|---|
| 25 | Fix MPS autocast (use float16 or remove) | `train.py:50-52` | 5 min |
| 26 | Add proper assertion messages | `train.py:705` | 10 min |
| 27 | Document weight decay asymmetry (intentional or bug?) | `train.py` | 10 min |
| 28 | Add structured experiment logging (JSON, not just TSV) | New utility | 2 hours |
| 29 | Pin all dependency versions for reproducibility | `pyproject.toml` | 10 min |
| 30 | Add CUDA/MPS memory estimation before training starts | `train.py` | 1 hour |

---

## 8. Summary Scorecard

| Category | Score | Max | Details |
|---|---|---|---|
| Correctness | 3/20 | 20 | Critical forward pass bug, missing files |
| Completeness | 5/15 | 15 | IGT system 0% implemented, missing `run_igt.py` and `program.md` |
| Security | 5/10 | 10 | Pickle deserialization, no checksum verification |
| Documentation | 5/15 | 15 | Inconsistent, duplicated, references non-existent files |
| Code Quality | 10/15 | 15 | Well-structured ML code, but dead variables, redundancy |
| Testing | 0/10 | 10 | Zero test coverage |
| Dependencies | 5/5 | 5 | Mostly clean, 2 unnecessary packages |
| Architecture | 5/10 | 10 | Good separation of concerns, missing checkpointing and isolation |
| **Total** | **38/100** | **100** | |

---

*Generated by comprehensive static and dynamic code analysis audit.*
