#!/usr/bin/env python3
"""Tiny terminal-based Minecraft-inspired sandbox."""
from __future__ import annotations

import argparse
import random
from dataclasses import dataclass, field
from typing import List, Tuple


Block = str
Position = Tuple[int, int]


@dataclass
class World:
    width: int
    height: int
    seed: int | None = None
    grid: List[List[Block]] = field(init=False)
    player: Position = field(init=False)

    def __post_init__(self) -> None:
        rng = random.Random(self.seed)
        self.grid = [["." for _ in range(self.width)] for _ in range(self.height)]
        self.player = (self.width // 2, self.height // 2)
        for _ in range((self.width * self.height) // 5):
            x = rng.randrange(self.width)
            y = rng.randrange(self.height)
            self.grid[y][x] = "#"
        self.grid[self.player[1]][self.player[0]] = "@"

    def in_bounds(self, position: Position) -> bool:
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def move_player(self, dx: int, dy: int) -> bool:
        x, y = self.player
        new_pos = (x + dx, y + dy)
        if not self.in_bounds(new_pos):
            return False
        self.grid[y][x] = "."
        self.player = new_pos
        self.grid[new_pos[1]][new_pos[0]] = "@"
        return True

    def place_block(self, block: Block) -> bool:
        x, y = self.player
        if self.grid[y][x] == "@":
            self.grid[y][x] = block
            self.player = (x, y)
            self.grid[y][x] = "@"
            return True
        return False

    def remove_block(self) -> None:
        x, y = self.player
        self.grid[y][x] = "@"

    def render(self) -> str:
        return "\n".join(" ".join(row) for row in self.grid)


COMMANDS = {
    "w": (0, -1),
    "a": (-1, 0),
    "s": (0, 1),
    "d": (1, 0),
}


def run_interactive(world: World) -> None:
    print("TinyCraft - move with WASD, place block with 'p', remove with 'r', quit with 'q'.")
    while True:
        print("\n" + world.render())
        command = input("Command: ").strip().lower()
        if command == "q":
            print("Thanks for playing!")
            break
        if command in COMMANDS:
            moved = world.move_player(*COMMANDS[command])
            if not moved:
                print("You bumped into the boundary.")
            continue
        if command == "p":
            world.place_block("#")
            continue
        if command == "r":
            world.remove_block()
            continue
        print("Unknown command.")


def run_demo(world: World, steps: int) -> None:
    rng = random.Random(world.seed)
    for _ in range(steps):
        dx, dy = rng.choice(list(COMMANDS.values()))
        world.move_player(dx, dy)
    print(world.render())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TinyCraft: a minimal Minecraft-inspired sandbox.")
    parser.add_argument("--width", type=int, default=10, help="World width in blocks.")
    parser.add_argument("--height", type=int, default=10, help="World height in blocks.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for terrain generation.")
    parser.add_argument("--demo", action="store_true", help="Run a non-interactive demo.")
    parser.add_argument("--steps", type=int, default=8, help="Demo steps to simulate.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    world = World(args.width, args.height, args.seed)
    if args.demo:
        run_demo(world, args.steps)
    else:
        run_interactive(world)


if __name__ == "__main__":
    main()
