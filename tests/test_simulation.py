from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from context_gridworld.agents import Context, EqualWeightAgent, ReliabilityAwareAgent
from context_gridworld.environment import GridWorld, GridWorldConfig
from context_gridworld.experiment import run_experiment, write_csv


class SimulationTests(unittest.TestCase):
    def test_reliability_agent_changes_weights_with_context_quality(self) -> None:
        agent = ReliabilityAwareAgent()
        high_quality = Context(
            current_position=(0, 0),
            goal_position=(2, 2),
            observed_obstacles=set(),
            stale_obstacles=set(),
            movement_history=[(0, 0)],
            sensor_reliability=0.9,
            stale_map_age=1,
        )
        low_quality = Context(
            current_position=(0, 0),
            goal_position=(2, 2),
            observed_obstacles=set(),
            stale_obstacles=set(),
            movement_history=[(0, 0)],
            sensor_reliability=0.2,
            stale_map_age=10,
        )

        self.assertGreater(
            agent.weights(high_quality).observed_obstacles,
            agent.weights(low_quality).observed_obstacles,
        )
        self.assertGreater(
            agent.weights(high_quality).stale_obstacles,
            agent.weights(low_quality).stale_obstacles,
        )

    def test_baseline_uses_equal_weights(self) -> None:
        context = Context(
            current_position=(0, 0),
            goal_position=(1, 1),
            observed_obstacles=set(),
            stale_obstacles=set(),
            movement_history=[],
            sensor_reliability=0.1,
            stale_map_age=100,
        )
        weights = EqualWeightAgent().weights(context)
        self.assertEqual(weights.goal, 1.0)
        self.assertEqual(weights.observed_obstacles, 1.0)
        self.assertEqual(weights.stale_obstacles, 1.0)
        self.assertEqual(weights.history, 1.0)

    def test_environment_blocks_obstacle_collision(self) -> None:
        world = GridWorld(GridWorldConfig(width=3, height=3, goal=(2, 2)), {(1, 0)})
        result = world.step((0, 0), "right")
        self.assertTrue(result.collided)
        self.assertEqual(result.position, (0, 0))

    def test_experiment_writes_expected_csv_rows(self) -> None:
        results = run_experiment(
            episodes=3,
            seed=7,
            sensor_noise=0.25,
            stale_map_age=5,
        )
        self.assertEqual(len(results), 6)

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "results.csv"
            write_csv(results, output)
            with output.open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 6)
        self.assertIn("success", rows[0])
        self.assertIn("collisions", rows[0])
        self.assertIn("steps", rows[0])


if __name__ == "__main__":
    unittest.main()
