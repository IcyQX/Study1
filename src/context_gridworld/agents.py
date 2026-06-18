from __future__ import annotations

from dataclasses import dataclass, field
from math import inf
from random import Random

from .environment import GridWorld, Position


@dataclass
class Context:
    current_position: Position
    goal_position: Position
    observed_obstacles: set[Position]
    stale_obstacles: set[Position]
    movement_history: list[Position]
    sensor_reliability: float
    stale_map_age: int


@dataclass
class ContextWeights:
    goal: float
    observed_obstacles: float
    stale_obstacles: float
    history: float


@dataclass
class EpisodeResult:
    agent: str
    episode: int
    success: bool
    collisions: int
    steps: int
    final_x: int
    final_y: int
    sensor_reliability: float
    stale_map_age: int


class BaseAgent:
    name = "base"

    def weights(self, context: Context) -> ContextWeights:
        raise NotImplementedError

    def choose_action(self, world: GridWorld, context: Context, rng: Random) -> str:
        weights = self.weights(context)
        scored_actions: list[tuple[float, str]] = []

        for action, candidate in world.neighbors(context.current_position).items():
            score = self._score_position(candidate, context, weights)
            scored_actions.append((score, action))

        best_score = max(score for score, _ in scored_actions)
        best_actions = [action for score, action in scored_actions if score == best_score]
        return rng.choice(sorted(best_actions))

    def _score_position(
        self,
        position: Position,
        context: Context,
        weights: ContextWeights,
    ) -> float:
        distance_score = -manhattan(position, context.goal_position)
        observed_penalty = -10.0 if position in context.observed_obstacles else 0.0
        stale_penalty = -10.0 if position in context.stale_obstacles else 0.0
        revisit_penalty = -1.0 if position in context.movement_history[-6:] else 0.0

        return (
            weights.goal * distance_score
            + weights.observed_obstacles * observed_penalty
            + weights.stale_obstacles * stale_penalty
            + weights.history * revisit_penalty
        )


class EqualWeightAgent(BaseAgent):
    name = "baseline_equal_weight"

    def weights(self, context: Context) -> ContextWeights:
        return ContextWeights(
            goal=1.0,
            observed_obstacles=1.0,
            stale_obstacles=1.0,
            history=1.0,
        )


class ReliabilityAwareAgent(BaseAgent):
    name = "proposed_reliability_aware"

    def weights(self, context: Context) -> ContextWeights:
        freshness = 1.0 / (1.0 + context.stale_map_age)
        sensor = clamp(context.sensor_reliability, 0.0, 1.0)

        return ContextWeights(
            goal=1.0,
            observed_obstacles=0.3 + 1.7 * sensor,
            stale_obstacles=0.2 + 1.4 * freshness,
            history=0.8,
        )


@dataclass
class EpisodeRunner:
    world: GridWorld
    stale_obstacles: set[Position]
    rng: Random = field(default_factory=Random)

    def run(self, agent: BaseAgent, episode: int) -> EpisodeResult:
        position = self.world.config.start
        history = [position]
        collisions = 0
        sensor_noise = self.world.config.sensor_noise
        sensor_reliability = 1.0 - sensor_noise

        for step in range(1, self.world.config.max_steps + 1):
            observed_obstacles = self.world.observe_obstacles(self.rng, sensor_noise)
            context = Context(
                current_position=position,
                goal_position=self.world.config.goal,
                observed_obstacles=observed_obstacles,
                stale_obstacles=self.stale_obstacles,
                movement_history=history,
                sensor_reliability=sensor_reliability,
                stale_map_age=self.world.config.stale_map_age,
            )
            action = agent.choose_action(self.world, context, self.rng)
            result = self.world.step(position, action)
            position = result.position
            history.append(position)

            if result.collided:
                collisions += 1

            if result.reached_goal:
                return EpisodeResult(
                    agent=agent.name,
                    episode=episode,
                    success=True,
                    collisions=collisions,
                    steps=step,
                    final_x=position[0],
                    final_y=position[1],
                    sensor_reliability=sensor_reliability,
                    stale_map_age=self.world.config.stale_map_age,
                )

        return EpisodeResult(
            agent=agent.name,
            episode=episode,
            success=False,
            collisions=collisions,
            steps=self.world.config.max_steps,
            final_x=position[0],
            final_y=position[1],
            sensor_reliability=sensor_reliability,
            stale_map_age=self.world.config.stale_map_age,
        )


def manhattan(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def clamp(value: float, low: float, high: float) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value
