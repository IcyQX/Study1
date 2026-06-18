# Physical AI Context Reliability Prototype

This repository contains a minimal research prototype for studying dynamic
context management and reliability estimation in physical AI agents.

The current prototype uses a simple 2D grid world instead of a real robot. An
agent moves from a start cell to a goal cell while avoiding obstacles. Sensor
observations are noisy, and the agent must decide how much to trust different
context sources.

## Research Question

Can an agent reduce collisions and improve task success by changing context
weights according to reliability and freshness?

## Implemented Agents

- **Baseline agent**: uses all context sources with equal weight.
- **Reliability-aware agent**: changes context weights based on sensor
  reliability and stale environment information.

## Context Sources

The simulation tracks these context values:

- Current position
- Goal position
- Obstacle information
- Past movement history
- Sensor reliability
- Stale environment information

## Metrics

Each episode records:

- Agent type
- Episode number
- Success or failure
- Collision count
- Steps to finish
- Final position
- Sensor reliability
- Stale map age

Results are saved as CSV.

## Requirements

Python 3.10 or newer is recommended. The prototype uses only the Python
standard library.

If `python` is not found on Windows, install Python from python.org or the
Microsoft Store, then select that interpreter in VS Code. You do not need to
install Python itself inside this repository.

Optional virtual environment setup:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If `py` is not available but another Python executable is installed, replace
`py` with that executable path. After the environment is created, you can run
Python directly through:

```powershell
.\.venv\Scripts\python.exe --version
```

After activating the virtual environment, use `python` normally.

## Run Experiments

From the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m context_gridworld.experiment --episodes 50 --output results/experiment_results.csv
```

On macOS or Linux:

```bash
PYTHONPATH=src python -m context_gridworld.experiment --episodes 50 --output results/experiment_results.csv
```

The script prints summary statistics and writes per-episode results to the CSV
file.

## Run Tests

From the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## Notes

This is intentionally small. It is meant to be a first experimental scaffold
that can later be extended with ROS 2, richer sensor models, dynamic obstacles,
or real robot logs.
