# EmbodiedMind: A Multi-Agent Perception-Planning-Execution Closed-Loop System for Real-World Physical Environments

The project implements a complete closed-loop agent pipeline:

```text
RGB/Depth Observation
      |
      v
Perception Agent ---> Structured World State
      |
      v
Planner Agent ---> Symbolic Plan
      |
      v
Critic Agent ---> Constraint / Reachability / Collision Validation
      |
      v
Action Agent ---> Action DSL Executor
      |
      v
Robot/Simulator Feedback
      |
      v
Reflection Agent ---> Local Re-planning on failure
```

Unlike a simple prompt demo, this repository contains:

- Configurable agents and environment backends
- A structured world model with spatial reasoning
- Action DSL with schema validation
- Perception model adapters (color segmentation, extensible to deep models)
- Tabletop simulation backend with noise modeling
- Evaluation scripts with comprehensive metrics
- Ablation experiments comparing baselines
- Reproducible task JSON definitions
- CLI demo and structured experiment logging

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Evaluation & Ablation](#evaluation--ablation)
- [Design Notes](#design-notes)
- [Extending EmbodiedMind](#extending-embodiedmind)
- [Requirements](#requirements)
- [License](#license)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/Pioneer6gun9/EmbodiedMind.git
cd EmbodiedMind

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"
```

---

## Quick Start

### 1. Run the Default Demo

```bash
# Option A: directly via Python
python examples/run_red_block_blue_box.py

# Option B: via shell script
bash scripts/run_demo.sh
```

Expected output:

```text
[2026-04-30 14:21:08] [PerceptionAgent] detected objects: red_block, blue_box, obstacle
[2026-04-30 14:21:09] [WorldModel] red_block: left_of=blue_box, reachable=True
[2026-04-30 14:21:10] [PlannerAgent] plan: locate -> approach -> grasp -> lift -> place
[2026-04-30 14:21:11] [CriticAgent] validated grasp(red_block): reachable=True collision=False
[2026-04-30 14:21:13] [ActionAgent] executed grasp(red_block): success
[2026-04-30 14:21:16] [ReflectionAgent] placement offset detected, local replan triggered
[2026-04-30 14:21:20] [Task] SUCCESS: red_block inside blue_box
```

### 2. Run Evaluation (100 episodes)

```bash
# Option A: directly via Python
python evaluation/run_eval.py --config configs/eval_red_block_blue_box.yaml --episodes 100

# Option B: via shell script
bash scripts/run_eval.sh
```

### 3. Run Ablation Study

```bash
bash scripts/reproduce_table1.sh
```

Outputs are saved under `runs/`.

---

## Configuration

All configs are written in YAML and live under `configs/`.

| File | Purpose |
|------|---------|
| `configs/tabletop.yaml` | Main config: environment, robot parameters, agent settings, logging |
| `configs/agents.yaml` | Agent input/output interface definitions |
| `configs/eval_red_block_blue_box.yaml` | Evaluation config (inherits `tabletop.yaml`, defines metrics & baselines) |

### Key Config Parameters (`configs/tabletop.yaml`)

```yaml
seed: 42                          # Random seed for reproducibility
env:
  backend: tabletop
  workspace:
    xlim: [-0.45, 0.45]           # Table X range (meters)
    ylim: [-0.30, 0.30]           # Table Y range (meters)
  robot:
    reach_radius: 0.55            # Maximum reach distance (meters)
    gripper_width: 0.08           # Gripper opening (meters)
    action_noise: 0.012           # Execution noise (meters)
    placement_noise: 0.018        # Placement noise (meters)
agents:
  perception:
    model: color_segmentation
    confidence_threshold: 0.65
  planner:
    max_steps: 8
  critic:
    check_reachability: true
    check_collision: true
  reflection:
    max_replans: 3                # Maximum local re-plan attempts
```

### Task Definitions

Tasks are defined as JSON files under `tasks/`. Example (`tasks/red_block_blue_box.json`):

```json
{
  "id": "red_block_blue_box",
  "language_instruction": "Place the red block into the blue box.",
  "objects": [
    {"id": "red_block", "type": "block", "color": "red", "size": [0.04, 0.04, 0.04], "initial_pose": [-0.18, 0.08, 0.02]},
    {"id": "blue_box", "type": "container", "color": "blue", "size": [0.12, 0.12, 0.06], "initial_pose": [0.2, -0.04, 0.03]},
    {"id": "obstacle", "type": "cylinder", "color": "gray", "size": [0.05, 0.05, 0.1], "initial_pose": [0.02, 0.02, 0.05]}
  ],
  "goal": {"predicate": "inside", "object": "red_block", "target": "blue_box"}
}
```

---

## Project Structure

```text
EmbodiedMind/
├── configs/                        # YAML configuration files
│   ├── agents.yaml                 # Agent I/O interface definitions
│   ├── tabletop.yaml               # Main environment & agent config
│   └── eval_red_block_blue_box.yaml# Evaluation config
├── embodiedmind/                   # Core library
│   ├── agents/                     # Five specialized agents
│   │   ├── perception_agent.py     # Visual observation -> world state
│   │   ├── planner_agent.py        # Task + state -> symbolic plan
│   │   ├── critic_agent.py         # Action validation (reachability, collision)
│   │   ├── action_agent.py         # DSL action execution
│   │   └── reflection_agent.py     # Failure diagnosis & local replanning
│   ├── dsl/                        # Action DSL
│   │   ├── action_schema.py        # Typed action definitions (Pydantic)
│   │   └── executor.py             # Action executor
│   ├── envs/                       # Environment backends
│   │   ├── tabletop_env.py         # Tabletop simulation
│   │   └── robot_interface.py      # Robot abstraction layer
│   ├── models/                     # Model adapters
│   │   ├── perception_model.py     # Perception (color segmentation, extensible)
│   │   └── llm_client.py          # LLM client (rule-based, extensible)
│   ├── policies/                   # Execution policies
│   │   ├── pick_place_policy.py    # Pick-and-place strategy
│   │   ├── constraint_checker.py   # Constraint validation
│   │   └── recovery_policy.py      # Recovery from failures
│   ├── world/                      # World modeling
│   │   ├── world_state.py          # Structured world state (Pydantic)
│   │   ├── object_registry.py      # Object tracking & registry
│   │   └── spatial_reasoner.py     # Spatial relation reasoning
│   ├── system.py                   # Top-level closed-loop orchestrator
│   └── utils/                      # Utilities
│       ├── config.py               # YAML config loader
│       └── logger.py               # Structured run logger (Rich)
├── evaluation/                     # Benchmarking & analysis
│   ├── run_eval.py                 # Main evaluation runner
│   ├── ablation.py                 # Ablation study (3 baselines)
│   └── metrics.py                  # Evaluation metrics
├── tasks/                          # Task definitions (JSON)
│   └── red_block_blue_box.json     # Default task
├── examples/                       # Demo entrypoints
│   └── run_red_block_blue_box.py   # Single-episode demo
├── scripts/                        # Reproduction scripts
│   ├── run_demo.sh                 # Run demo
│   ├── run_eval.sh                 # Run evaluation
│   └── reproduce_table1.sh         # Reproduce ablation table
├── tests/                          # Unit tests
│   ├── test_action_schema.py
│   └── test_world_state.py
├── runs/                           # Output directory (gitignored)
├── pyproject.toml                  # Package metadata
├── requirements.txt                # Python dependencies
└── README.md
```

---


## Evaluation & Ablation

### Run Full Evaluation

```bash
# 100-episode evaluation with randomization
python evaluation/run_eval.py --config configs/eval_red_block_blue_box.yaml --episodes 100

# Ablation study
python evaluation/ablation.py --episodes 100 --out runs/table1_ablation.json
```

Results are saved as JSON under `runs/`.

---

## Design Notes

### Why Multiple Agents?

The system separates concerns across five specialized agents:

- **PerceptionAgent** converts raw visual observations into a structured, symbolic world state.
- **PlannerAgent** generates task-level symbolic plans from natural language instructions.
- **CriticAgent** pre-validates actions for reachability and collision before execution.
- **ActionAgent** executes validated actions through a typed DSL.
- **ReflectionAgent** diagnoses failures and performs local replanning without restarting from scratch.

### Why Use an Action DSL?

LLMs should not directly control low-level motors. EmbodiedMind restricts high-level decisions into a typed action space:

```json
{"name": "grasp", "target": "red_block"}
{"name": "place", "target": "red_block", "container": "blue_box"}
```

This enables:
- **Schema validation** via Pydantic models
- **Safety checks** before execution
- **Reproducible execution** with structured logging

---

## Extending EmbodiedMind

### Adding a New Task

Create a JSON file under `tasks/`:

```json
{
  "id": "my_task",
  "language_instruction": "Stack the green cube on the yellow cylinder.",
  "objects": [...],
  "goal": {"predicate": "on_top", "object": "green_cube", "target": "yellow_cylinder"}
}
```

### Adding a New Perception Model

Implement the perception model interface and register it in `embodiedmind/models/perception_model.py`.

### Connecting a Real Robot

Implement the `robot_interface.py` abstraction layer to bridge EmbodiedMind's action DSL to your robot's SDK.

---
