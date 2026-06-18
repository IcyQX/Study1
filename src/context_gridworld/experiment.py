from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from pathlib import Path
from random import Random

from .agents import EqualWeightAgent, EpisodeResult, EpisodeRunner, ReliabilityAwareAgent
from .environment import GridWorld, GridWorldConfig, default_obstacles


def make_stale_obstacles(true_obstacles: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """Create an outdated map that still contains removed old obstacles."""
    stale = set(true_obstacles)
    stale.add((2, 4))
    stale.add((6, 7))
    return stale


def run_experiment(
    episodes: int,
    seed: int,
    sensor_noise: float,
    stale_map_age: int,
) -> list[EpisodeResult]:
    config = GridWorldConfig(sensor_noise=sensor_noise, stale_map_age=stale_map_age)
    true_obstacles = default_obstacles()
    world = GridWorld(config=config, obstacles=true_obstacles)
    stale_obstacles = make_stale_obstacles(true_obstacles)

    results: list[EpisodeResult] = []
    agents = [EqualWeightAgent(), ReliabilityAwareAgent()]

    for agent_index, agent in enumerate(agents):
        runner = EpisodeRunner(
            world=world,
            stale_obstacles=stale_obstacles,
            rng=Random(seed + agent_index * 10_000),
        )
        for episode in range(1, episodes + 1):
            results.append(runner.run(agent, episode))

    return results


def write_csv(results: list[EpisodeResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(results[0]).keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(asdict(result))


def summarize(results: list[EpisodeResult]) -> str:
    lines = ["agent, episodes, success_rate, avg_collisions, avg_steps"]
    by_agent: dict[str, list[EpisodeResult]] = {}
    for result in results:
        by_agent.setdefault(result.agent, []).append(result)

    for agent, agent_results in sorted(by_agent.items()):
        count = len(agent_results)
        success_rate = sum(result.success for result in agent_results) / count
        avg_collisions = sum(result.collisions for result in agent_results) / count
        avg_steps = sum(result.steps for result in agent_results) / count
        lines.append(
            f"{agent}, {count}, {success_rate:.3f}, "
            f"{avg_collisions:.3f}, {avg_steps:.3f}"
        )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run grid-world context experiments.")
    parser.add_argument("--episodes", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--sensor-noise", type=float, default=0.25)
    parser.add_argument("--stale-map-age", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/experiment_results.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = run_experiment(
        episodes=args.episodes,
        seed=args.seed,
        sensor_noise=args.sensor_noise,
        stale_map_age=args.stale_map_age,
    )
    write_csv(results, args.output)
    print(summarize(results))
    print(f"wrote CSV: {args.output}")


if __name__ == "__main__":
    main()
