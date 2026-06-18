# Repository Guidance

This repository is for master's research on dynamic context management and
reliability estimation for physical AI agents.

## Project Focus

- Keep the research scope centered on indoor mobile robots or autonomous
  mobile agents.
- Prioritize implementations that can be evaluated in simulation before
  requiring real hardware.
- Treat sensor data, maps, action history, human instructions, and environment
  state as separate context sources with explicit metadata.
- When adding experiments, include clear assumptions, failure cases, and
  measurable evaluation criteria.

## Implementation Guidelines

- Prefer small, reproducible prototypes over broad, hard-to-evaluate systems.
- Keep experiment scripts deterministic where practical by exposing random
  seeds and scenario configuration.
- Store generated outputs under `outputs/`, `runs/`, or `results/` and avoid
  committing large generated files unless they are small summary artifacts.
- Document dependencies and commands when adding executable code.
- Avoid hard-coding local absolute paths, credentials, API keys, or machine-
  specific settings.

## Research Notes

- Distinguish clearly between baseline methods and proposed methods.
- Record evaluation metrics such as task success rate, collision count, near
  miss count, path length, completion time, replanning count, and confidence
  calibration error.
- When using external papers, datasets, or libraries, cite their source in the
  relevant note, README, or experiment file.
- For Japanese research notes, keep terminology consistent and define key
  terms near the start of the document.

## Review Guidelines

- Check whether proposed changes preserve reproducibility.
- Flag experiment code that cannot be rerun from documented commands.
- Flag evaluation claims that do not connect to a metric, scenario, or baseline.
- Flag unsafe robot behavior assumptions, especially when uncertainty is high
  but the policy still proceeds without stopping, replanning, or re-observing.
- Treat accidental commits of secrets, local paths, large logs, datasets, or
  generated binaries as high-priority issues.
