from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterable


Position = tuple[int, int]


@dataclass(frozen=True)
class GridWorldConfig:
    width: int = 10
    height: int = 10
    start: Position = (0, 0)
    goal: Position = (9, 9)
    max_steps: int = 60
    sensor_noise: float = 0.2
    stale_map_age: int = 5


@dataclass(frozen=True)
class StepResult:
    position: Position
    collided: bool
    reached_goal: bool


class GridWorld:
    """Small deterministic grid world with noisy obstacle observations."""

    ACTIONS: dict[str, Position] = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0),
        "stay": (0, 0),
    }

    def __init__(self, config: GridWorldConfig, obstacles: Iterable[Position]):
        self.config = config
        self.obstacles = set(obstacles)

    def in_bounds(self, position: Position) -> bool:
        x, y = position
        return 0 <= x < self.config.width and 0 <= y < self.config.height

    def is_obstacle(self, position: Position) -> bool:
        return position in self.obstacles

    def neighbors(self, position: Position) -> dict[str, Position]:
        result: dict[str, Position] = {}
        x, y = position
        for action, (dx, dy) in self.ACTIONS.items():
            candidate = (x + dx, y + dy)
            if self.in_bounds(candidate):
                result[action] = candidate
        return result

    def step(self, position: Position, action: str) -> StepResult:
        if action not in self.ACTIONS:
            raise ValueError(f"unknown action: {action}")

        dx, dy = self.ACTIONS[action]
        candidate = (position[0] + dx, position[1] + dy)
        if not self.in_bounds(candidate):
            candidate = position

        collided = self.is_obstacle(candidate)
        next_position = position if collided else candidate
        return StepResult(
            position=next_position,
            collided=collided,
            reached_goal=next_position == self.config.goal,
        )

    def observe_obstacles(self, rng: Random, sensor_noise: float) -> set[Position]:
        """Return a noisy obstacle set with false negatives and false positives."""
        observed: set[Position] = set()
        for obstacle in self.obstacles:
            if rng.random() >= sensor_noise:
                observed.add(obstacle)

        free_cells = [
            (x, y)
            for x in range(self.config.width)
            for y in range(self.config.height)
            if (x, y) not in self.obstacles
            and (x, y) not in {self.config.start, self.config.goal}
        ]
        false_positive_count = int(len(self.obstacles) * sensor_noise * 0.5)
        rng.shuffle(free_cells)
        observed.update(free_cells[:false_positive_count])
        return observed


def default_obstacles() -> set[Position]:
    """Obstacle layout with a narrow passage to make context choice matter."""
    return {
        (2, 0),
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 5),
        (2, 6),
        (4, 4),
        (5, 4),
        (6, 4),
        (7, 4),
        (7, 5),
        (7, 6),
        (7, 7),
        (3, 8),
        (4, 8),
        (5, 8),
    }
