# TinyCraft (Minecraft-inspired sandbox)

This repo contains a tiny, terminal-based sandbox inspired by Minecraft. It generates a small block world, lets you move around, and place/remove blocks.

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

## Controls

- `w`, `a`, `s`, `d`: move
- `p`: place a block at the player location
- `r`: remove a block at the player location
- `q`: quit

## Notes

This is a minimal clone intended to be easy to run and extend.
