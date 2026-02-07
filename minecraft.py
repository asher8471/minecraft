#!/usr/bin/env python3
"""Tiny terminal-based Minecraft-inspired sandbox."""
from __future__ import annotations

import argparse
import json
import random
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


Position = Tuple[int, int]


BLOCKS = {
    ".": {"name": "Air", "solid": False},
    "#": {"name": "Stone", "solid": True},
    ",": {"name": "Dirt", "solid": True},
    "T": {"name": "Tree", "solid": True},
    "W": {"name": "Water", "solid": False},
    "*": {"name": "Ore", "solid": True},
}

RECIPE_BOOK: Dict[str, Dict[str, int]] = {
    "plank": {"tree": 1},
    "stick": {"plank": 2},
    "torch": {"stick": 1, "coal": 1},
    "pickaxe": {"stick": 2, "ore": 3},
}


@dataclass
class Player:
    hp: int = 10
    hunger: int = 10
    inventory: Dict[str, int] = field(default_factory=lambda: {"dirt": 0, "stone": 0, "tree": 0, "ore": 0, "coal": 0})
    tools: Dict[str, int] = field(default_factory=dict)

    def add_item(self, item: str, count: int = 1) -> None:
        self.inventory[item] = self.inventory.get(item, 0) + count

    def consume_item(self, item: str, count: int = 1) -> bool:
        if self.inventory.get(item, 0) < count:
            return False
        self.inventory[item] -= count
        return True

    def add_tool(self, tool: str, durability: int = 10) -> None:
        self.tools[tool] = max(self.tools.get(tool, 0), durability)

    def damage_tool(self, tool: str) -> None:
        if tool not in self.tools:
            return
        self.tools[tool] -= 1
        if self.tools[tool] <= 0:
            del self.tools[tool]


@dataclass
class World:
    width: int
    height: int
    seed: int | None = None
    grid: List[List[str]] = field(init=False)
    player_pos: Position = field(init=False)
    day: int = 1

    def __post_init__(self) -> None:
        rng = random.Random(self.seed)
        self.grid = [["." for _ in range(self.width)] for _ in range(self.height)]
        self.player_pos = (self.width // 2, self.height // 2)
        for y in range(self.height):
            for x in range(self.width):
                roll = rng.random()
                if roll < 0.07:
                    self.grid[y][x] = "W"
                elif roll < 0.18:
                    self.grid[y][x] = ","
                elif roll < 0.23:
                    self.grid[y][x] = "T"
                elif roll < 0.28:
                    self.grid[y][x] = "*"
                elif roll < 0.55:
                    self.grid[y][x] = "#"
        self.grid[self.player_pos[1]][self.player_pos[0]] = "@"

    def in_bounds(self, position: Position) -> bool:
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def move_player(self, dx: int, dy: int) -> bool:
        x, y = self.player_pos
        new_pos = (x + dx, y + dy)
        if not self.in_bounds(new_pos):
            return False
        if self.grid[new_pos[1]][new_pos[0]] in {"#", "T", "*"}:
            return False
        self.grid[y][x] = "."
        self.player_pos = new_pos
        self.grid[new_pos[1]][new_pos[0]] = "@"
        return True

    def get_block(self, position: Position) -> str:
        x, y = position
        return self.grid[y][x]

    def set_block(self, position: Position, block: str) -> None:
        x, y = position
        self.grid[y][x] = block

    def render(self, vision: int = 6) -> str:
        px, py = self.player_pos
        output: List[str] = []
        for y in range(max(0, py - vision), min(self.height, py + vision + 1)):
            row = self.grid[y][max(0, px - vision) : min(self.width, px + vision + 1)]
            output.append(" ".join(row))
        return "\n".join(output)


COMMANDS = {
    "w": (0, -1),
    "a": (-1, 0),
    "s": (0, 1),
    "d": (1, 0),
}


def gather_drop(block: str, rng: random.Random) -> str | None:
    if block == "#":
        return "stone"
    if block == ",":
        return "dirt"
    if block == "T":
        return "tree"
    if block == "*":
        return "ore" if rng.random() < 0.7 else "coal"
    return None


def mining_power(player: Player) -> int:
    return 2 if "pickaxe" in player.tools else 1


def placeable_blocks(player: Player) -> List[str]:
    return [item for item in ("dirt", "stone", "tree") if player.inventory.get(item, 0) > 0]


def stats_line(player: Player, world: World) -> str:
    tools = ", ".join(f"{name}({dur})" for name, dur in player.tools.items()) or "none"
    return f"Day {world.day} | HP {player.hp}/10 | Hunger {player.hunger}/10 | Tools: {tools}"


def inventory_lines(player: Player) -> List[str]:
    lines = ["Inventory:"]
    for item, count in sorted(player.inventory.items()):
        lines.append(f"- {item}: {count}")
    if player.tools:
        lines.append("Tools:")
        for tool, dur in player.tools.items():
            lines.append(f"- {tool}: {dur}")
    return lines


def craft_item(player: Player, item: str) -> str:
    if item not in RECIPE_BOOK:
        return "Unknown recipe."
    recipe = RECIPE_BOOK[item]
    for ingredient, amount in recipe.items():
        if player.inventory.get(ingredient, 0) < amount:
            return f"Missing {ingredient}."
    for ingredient, amount in recipe.items():
        player.consume_item(ingredient, amount)
    if item == "pickaxe":
        player.add_tool("pickaxe", durability=12)
        return "Crafted a pickaxe."
    player.add_item(item, 1)
    return f"Crafted {item}."


def save_world(world: World, player: Player, path: str) -> str:
    data = {
        "world": {
            "width": world.width,
            "height": world.height,
            "seed": world.seed,
            "day": world.day,
            "grid": world.grid,
            "player_pos": world.player_pos,
        },
        "player": {
            "hp": player.hp,
            "hunger": player.hunger,
            "inventory": player.inventory,
            "tools": player.tools,
        },
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
    return f"Saved to {path}."


def load_world(path: str) -> Tuple[World, Player]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    world_data = data["world"]
    world = World(world_data["width"], world_data["height"], world_data["seed"])
    world.grid = world_data["grid"]
    world.player_pos = tuple(world_data["player_pos"])  # type: ignore[assignment]
    world.day = world_data["day"]
    player_data = data["player"]
    player = Player(
        hp=player_data["hp"],
        hunger=player_data["hunger"],
        inventory=player_data["inventory"],
        tools=player_data["tools"],
    )
    return world, player


def advance_day(player: Player, world: World) -> None:
    world.day += 1
    player.hunger = max(0, player.hunger - 1)
    if player.hunger == 0:
        player.hp = max(0, player.hp - 1)


def run_interactive(world: World, player: Player, save_path: str | None) -> None:
    print(
        "\n".join(
            textwrap.wrap(
                "TinyCraft+ - move with WASD, mine with 'm', place with 'p', craft with 'c', "
                "rest with 'n', inventory with 'i', save with 'save', quit with 'q'.",
                width=88,
            )
        )
    )
    rng = random.Random(world.seed)
    while True:
        print("\n" + stats_line(player, world))
        print(world.render())
        command = input("Command: ").strip().lower()
        if command == "q":
            print("Thanks for playing!")
            break
        if command in COMMANDS:
            moved = world.move_player(*COMMANDS[command])
            if not moved:
                print("Blocked: obstacle or boundary.")
            continue
        if command == "i":
            print("\n".join(inventory_lines(player)))
            continue
        if command == "m":
            px, py = world.player_pos
            target = (px, max(0, py - 1))
            block = world.get_block(target)
            if block in {"#", ",", "T", "*"}:
                power = mining_power(player)
                drop = gather_drop(block, rng)
                world.set_block(target, ".")
                if drop:
                    player.add_item(drop, power)
                if block == "*" and "pickaxe" in player.tools:
                    player.damage_tool("pickaxe")
                print(f"Mined {BLOCKS[block]['name']}.")
            else:
                print("Nothing to mine.")
            continue
        if command == "p":
            placeables = placeable_blocks(player)
            if not placeables:
                print("No blocks to place.")
                continue
            chosen = placeables[0]
            px, py = world.player_pos
            target = (px, max(0, py - 1))
            if world.get_block(target) != ".":
                print("Space is occupied.")
                continue
            player.consume_item(chosen, 1)
            symbol = "," if chosen == "dirt" else "#" if chosen == "stone" else "T"
            world.set_block(target, symbol)
            print(f"Placed {chosen}.")
            continue
        if command == "c":
            recipe_list = ", ".join(RECIPE_BOOK.keys())
            choice = input(f"Craft what? ({recipe_list}) ").strip().lower()
            print(craft_item(player, choice))
            continue
        if command == "n":
            advance_day(player, world)
            print("You rest and a new day begins.")
            continue
        if command.startswith("save"):
            if not save_path:
                print("No save path configured.")
                continue
            print(save_world(world, player, save_path))
            continue
        print("Unknown command.")


def run_demo(world: World, player: Player, steps: int) -> None:
    rng = random.Random(world.seed)
    for _ in range(steps):
        dx, dy = rng.choice(list(COMMANDS.values()))
        world.move_player(dx, dy)
        if rng.random() < 0.3:
            advance_day(player, world)
    print(stats_line(player, world))
    print(world.render())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TinyCraft+: a minimal Minecraft-inspired sandbox.")
    parser.add_argument("--width", type=int, default=20, help="World width in blocks.")
    parser.add_argument("--height", type=int, default=12, help="World height in blocks.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for terrain generation.")
    parser.add_argument("--demo", action="store_true", help="Run a non-interactive demo.")
    parser.add_argument("--steps", type=int, default=10, help="Demo steps to simulate.")
    parser.add_argument("--load", type=str, default=None, help="Load world from a save file.")
    parser.add_argument("--save", type=str, default="savegame.json", help="Save file path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.load:
        world, player = load_world(args.load)
    else:
        world = World(args.width, args.height, args.seed)
        player = Player()
    if args.demo:
        run_demo(world, player, args.steps)
    else:
        run_interactive(world, player, args.save)


if __name__ == "__main__":
    main()
