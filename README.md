# TinyCraft+ (Minecraft-inspired sandbox)

TinyCraft+ is a terminal-based sandbox inspired by Minecraft. It generates a small world with resources, lets you explore, mine, craft, and save your progress.

## Requirements

- Python 3.10+

## Run

Interactive mode:

```bash
python minecraft.py
```

Non-interactive demo (useful for CI/testing):

```bash
python minecraft.py --demo --steps 12
```

Load a saved world:

```bash
python minecraft.py --load savegame.json
```

## Controls

- `w`, `a`, `s`, `d`: move
- `m`: mine the block above you
- `p`: place a block above you (uses inventory)
- `c`: craft an item from recipes
- `n`: rest and advance the day
- `i`: view inventory
- `save`: save the world
- `q`: quit

## Features

- Procedural terrain with stone, dirt, trees, ore, and water
- Mining drops resources and tools affect yield
- Crafting system with recipes (planks, sticks, torches, pickaxe)
- Day progression with hunger and health penalties
- Save/load support via JSON

## Notes

This is a small clone intended to be easy to run and extend.
