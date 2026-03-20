# Auto-Improvement System for Iowa Gambling Task Experiments

## Overview

The auto-improvement system adapts the autonomous research framework from the original autoresearch project (designed for LLM training) to psychological experimentation with the Iowa Gambling Task (IGT). Instead of optimizing neural network training metrics, it optimizes decision-making task sensitivity.

The idea: give an AI agent a small but real LLM training setup and let it experiment autonomously overnight. It modifies the code, trains for 5 minutes, checks if the result improved, keeps or discards, and repeats. You wake up in the morning to a log of experiments and (hopefully) a better model. The training code here is a simplified single-GPU implementation of [nanochat](https://github.com/karpathy/nanochat). The core idea is that you're not touching any of the Python files like you normally would as a researcher. Instead, you are programming the `program.md` Markdown files that provide context to the AI agents and set up your autonomous research org. The default `program.md` in this repo is intentionally kept as a bare bones baseline, though it's obvious how one would iterate on it over time to find the "research org code" that achieves the fastest research progress, how you'd add more agents to the mix, etc. A bit more context on this project is here in this [tweet](https://x.com/karpathy/status/2029701092347630069).

## How it works

The repo is deliberately kept small and only really has three files that matter:

- **`prepare.py`** — fixed constants, one-time data prep (downloads training data, trains a BPE tokenizer), and runtime utilities (dataloader, evaluation). Not modified.
- **`train.py`** — the single file the agent edits. Contains the full GPT model, optimizer (Muon + AdamW), and training loop. Everything is fair game: architecture, hyperparameters, optimizer, batch size, etc. **This file is edited and iterated on by the agent**.
- **`program.md`** — baseline instructions for one agent. Point your agent here and let it go. **This file is edited and iterated on by the human**.

By design, training runs for a **fixed 5-minute time budget** (wall clock, excluding startup/compilation), regardless of the details of your compute. The metric is **val_bpb** (validation bits per byte) — lower is better, and vocab-size-independent so architectural changes are fairly compared.

If you are new to neural networks, this ["Dummy's Guide"](https://x.com/hooeem/status/2030720614752039185) looks pretty good for a lot more context.

## Quick start

**Requirements:** A single NVIDIA GPU (tested on H100), Python 3.10+, [uv](https://docs.astral.sh/uv/).

```bash

# 1. Install uv project manager (if you don't already have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies
uv sync

# 3. Download data and train tokenizer (one-time, ~2 min)
uv run prepare.py

# 4. Manually run a single training experiment (~5 min)
uv run train.py
```

If the above commands all work ok, your setup is working and you can go into autonomous research mode.

## Running the agent

Simply spin up your Claude/Codex or whatever you want in this repo (and disable all permissions), then you can prompt something like:

```markdown
Hi have a look at program.md and let's kick off a new experiment! let's do the setup first.
```

The `program.md` file is essentially a super lightweight "skill".

## Project structure

```text
prepare.py      — constants, data prep + runtime utilities (do not modify)
train.py        — model, optimizer, training loop (agent modifies this)
program.md      — agent instructions
pyproject.toml  — dependencies
```

## Design choices

- **Single file to modify.** The agent only touches `train.py`. This keeps the scope manageable and diffs reviewable.
- **Fixed time budget.** Training always runs for exactly 5 minutes, regardless of your specific platform. This means you can expect approx 12 experiments/hour and approx 100 experiments while you sleep. There are two upsides of this design decision. First, this makes experiments directly comparable regardless of what the agent changes (model size, batch size, architecture, etc). Second, this means that autoresearch will find the most optimal model for your platform in that time budget. The downside is that your runs (and results) become not comparable to other people running on other compute platforms.
- **Self-contained.** No external dependencies beyond PyTorch and a few small packages. No distributed training, no complex configs. One GPU, one file, one metric.

## Platform support

This code currently requires that you have a single NVIDIA GPU. In principle it is quite possible to support CPU, MPS and other platforms but this would also bloat the code. I'm not 100% sure that I want to take this on personally right now. People can reference (or have their agents reference) the full/parent nanochat repository that has wider platform support and shows the various solutions (e.g. a Flash Attention 3 kernels fallback implementation, generic device support, autodetection, etc.), feel free to create forks or discussions for other platforms and I'm happy to link to them here in the README in some new notable forks section or etc.

Seeing as there seems to be a lot of interest in tinkering with autoresearch on much smaller compute platforms than an H100, a few extra words. If you're going to try running autoresearch on smaller computers (Macbooks etc.), I'd recommend one of the forks below. On top of this, here are some recommendations for how to tune the defaults for much smaller models for aspiring forks:

1. To get half-decent results I'd use a dataset with a lot less entropy, e.g. this [TinyStories dataset](https://huggingface.co/datasets/karpathy/tinystories-gpt4-clean). These are GPT-4 generated short stories. Because the data is a lot narrower in scope, you will see reasonable results with a lot smaller models (if you try to sample from them after training).
2. You might experiment with decreasing `vocab_size`, e.g. from 8192 down to 4096, 2048, 1024, or even - simply byte-level tokenizer with 256 possibly bytes after utf-8 encoding.
3. In `prepare.py`, you'll want to lower `MAX_SEQ_LEN` a lot, depending on the computer even down to 256 etc. As you lower `MAX_SEQ_LEN`, you may want to experiment with increasing `DEVICE_BATCH_SIZE` in `train.py` slightly to compensate. The number of tokens per fwd/bwd pass is the product of these two.
4. Also in `prepare.py`, you'll want to decrease `EVAL_TOKENS` so that your validation loss is evaluated on a lot less data.
5. In `train.py`, the primary single knob that controls model complexity is the `DEPTH` (default 8, here). A lot of variables are just functions of this, so e.g. lower it down to e.g. 4.
6. You'll want to most likely use `WINDOW_PATTERN` of just "L", because "SSSL" uses alternating banded attention pattern that may be very inefficient for you. Try it.
7. You'll want to lower `TOTAL_BATCH_SIZE` a lot, but keep it powers of 2, e.g. down to `2**14` (~16K) or so even, hard to tell.

It would be the reasonable hyperparameters to play with. Ask your favorite coding agent for help and copy paste them this guide, as well as the full source code.

## Core Architecture Comparison

### Original Autoresearch System

- **`prepare.py`** - Fixed data prep and utilities (read-only)
- **`train.py`** - Model and training code (agent-modified)
- **`EXPERIMENT.md`** - Agent instructions (human-modified)
- **Goal**: Minimize validation bits per byte (val_bpb)
- **Time Budget**: 5 minutes per experiment

### IGT Adaptation

- **`prepare.py`** - Fixed IGT deck configurations and metrics (read-only)
- **`run_igt.py`** - Task parameters and trial logic (agent-modified)
- **`iowa.md`** - Experiment instructions (human-modified)
- **Goal**: Maximize net score (advantageous - disadvantageous choices)
- **Time Budget**: 10 minutes per experiment

## Step-by-Step Setup Instructions

### Phase 1: Initial Setup

#### Create Experiment Branch

```bash
# Generate tag based on current date
TAG=$(date +%b%d | tr '[:upper:]' '[:lower:]')  # e.g., mar20

# Check if branch exists
if git show-ref --verify --quiet refs/heads/igt/$TAG; then
    echo "Branch igt/$TAG already exists"
    TAG=$(date +%b%d-%H%M)  # Add time if needed
fi

# Create and checkout branch
git checkout -b igt/$TAG
```

#### Read Context Files

- Read `USAGE.md` for repository context
- Read `prepare.py` to understand fixed constants and deck configurations
- Read `run_igt.py` to understand modifiable parameters

#### Verify Data Setup

```bash
# Check if stimuli data exists
if [ ! -d "data/stimuli" ]; then
    echo "Running data preparation..."
    uv run prepare.py
fi
```

#### Initialize Results Tracking

```bash
# Create results file with header
echo -e "commit\tnet_score\ttime_min\tmemory_gb\tstatus\tdescription" > results.tsv
```

### Phase 2: Autonomous Experiment Loop

The core innovation is the infinite autonomous loop that continuously optimizes the task:

**LOOP FOREVER:**

#### Check Git State

```bash
# Ensure clean working directory
if [ -n "$(git status --porcelain)" ]; then
    echo "Working directory not clean - committing changes"
    git add .
    git commit -m "Experiment checkpoint"
fi
```

#### Generate Experiment Idea

- Review previous results in `results.tsv`
- Identify promising modification directions
- Examples: adjust reward magnitudes, modify feedback delays, change trial counts

#### Modify `run_igt.py`

- Edit task parameters within allowed scope
- Maintain core IGT logic integrity
- Log modification description

#### Commit Changes

```bash
git add run_igt.py
git commit -m "Experiment: [description]"
```

#### Execute Experiment

```bash
# Run with timeout and logging
timeout 15m uv run run_igt.py > run.log 2>&1
EXIT_CODE=$?
```

#### Extract Results

```bash
# Parse key metrics from log
net_score=$(grep "^net_score:" run.log | awk '{print $2}')
completion_time=$(grep "^completion_time_s:" run.log | awk '{print $2}')
peak_memory=$(grep "^peak_vram_mb:" run.log | awk '{print $2}')

# Convert to required units
time_min=$(echo "$completion_time / 60" | bc -l | xargs printf "%.1f")
memory_gb=$(echo "$peak_memory / 1024" | bc -l | xargs printf "%.1f")
```

#### Handle Crashes/Timeouts

```bash
if [ $EXIT_CODE -eq 124 ]; then
    # Timeout - mark as failure
    echo "Experiment timed out"
    status="crash"
elif [ $EXIT_CODE -ne 0 ]; then
    # Crash - check if trivial
    tail -n 50 run.log
    # If trivial error, fix and retry; otherwise mark as crash
    status="crash"
else
    status="keep"  # tentatively
fi
```

#### Record Results

```bash
commit_hash=$(git rev-parse --short HEAD)
echo -e "$commit_hash\t$net_score\t$time_min\t$memory_gb\t$status\t$description" >> results.tsv
```

#### Decision Logic

```bash
# Compare with previous best score
best_score=$(awk 'NR>1 && $5=="keep" {print $2}' results.tsv | sort -nr | head -1)

if (( $(echo "$net_score > $best_score" | bc -l) )); then
    echo "Improvement! Keeping commit"
    # Commit is already kept
else
    echo "No improvement. Resetting..."
    git reset --hard HEAD~1
fi
```

### Phase 3: Experiment Strategy

#### Allowed Modifications in `run_igt.py`

- **Task Parameters**: Number of trials, inter-trial intervals, deck selection probabilities
- **Reward Schedules**: Win/loss magnitudes, frequency distributions
- **Feedback Mechanisms**: Visual/auditory feedback timing, delay durations
- **Data Collection**: Additional metrics (reaction times, confidence ratings)
- **Analysis**: Learning curve calculations, statistical tests

#### Prohibited Modifications

- Changing core deck probabilities in `prepare.py`
- Adding external dependencies
- Modifying evaluation metric definition

#### Optimization Targets

- **Primary**: Net score (advantageous - disadvantageous deck selections)
- **Secondary**: Learning rate, completion time, memory efficiency

### Phase 4: Advanced Adaptations

#### For Psychological Research Integration

##### Stimulus Presentation Tools

```python
# Integrate with psychopy for precise timing
from psychopy import visual, core

# Replace simple feedback with psychopy stimuli
def show_feedback(win, outcome, deck_type):
    feedback_text = visual.TextStim(win, text=f"Outcome: {outcome}")
    feedback_text.draw()
    win.flip()
    core.wait(1.0)  # Controlled feedback duration
```

##### Advanced Data Analysis

```python
# Add statistical tests to run_igt.py
import scipy.stats as stats

def analyze_learning_curve(choices, outcomes):
    # Calculate learning rate across trial blocks
    blocks = np.array_split(choices, 5)  # 5 blocks
    learning_scores = [calculate_block_score(block) for block in blocks]
    
    # Test for significant learning trend
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        range(len(learning_scores)), learning_scores
    )
    return learning_rate, p_value
```

##### Reproducibility Enhancements

```python
# Log all random seeds and parameters
experiment_config = {
    'random_seed': np.random.randint(0, 10000),
    'deck_config': deck_configuration,
    'reward_schedule': reward_magnitudes,
    'feedback_delay': delay_duration,
    'timestamp': datetime.now().isoformat()
}
```

## Key Advantages

- **Autonomous Optimization**: Continuously improves task sensitivity without human intervention
- **Systematic Exploration**: Tests parameter combinations systematically
- **Reproducible Research**: Every change tracked with git and results logged
- **Time-Bounded Experiments**: Each run limited to 10 minutes for high-throughput testing
- **Adaptive to Platform**: Optimizes for specific hardware/time constraints

## Expected Workflow

- **Setup Phase** (30 minutes): Branch creation, data verification, baseline run
- **Autonomous Phase** (Overnight): ~60 experiments (6 hours × 6 experiments/hour)
- **Analysis Phase** (Morning): Review `results.tsv`, identify optimal configuration
- **Validation Phase**: Run final optimized configuration with multiple participants

This system transforms psychological task optimization from manual trial-and-error to autonomous, systematic exploration, potentially discovering novel parameter combinations that maximize task sensitivity for detecting decision-making differences.
