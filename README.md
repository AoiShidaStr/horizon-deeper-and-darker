# Deeper and Darker — Horizon port

A port of **Deeper and Darker** by **Kyanite Mods** (GPL-3.0-only) to
[Horizon](https://github.com/horizon-rust/horizon), Minecraft Java 26.3.
The upstream mod adds the Otherside dimension, sculk/echo/bloom materials and
gear, and the sculk mobs. This port ships a working slice of that on Horizon:

- a **content mod** (`.hmod`, no code) with the blocks, items, recipes, loot,
  sounds, language files and mob types;
- a **native mod** (`.hnmod`, Rust) with the sculk mobs' goals and the
  shriek worm's cycle.

Pinned Horizon revision: `a85af177a82504f357ff10d5d40d0b7230e2ac32`
(horizon-mixins `5a64af938ec86b00d53d16a408aabc0038fb3e57`).

## Layout

| Path | What |
| --- | --- |
| `content/horizon-mod.toml` | content mod manifest (id `deeperdarker`, API 0.2, side `both`) |
| `content/assets/deeperdarker/` | blockstates, models, item definitions, textures, sounds, lang |
| `content/data/deeperdarker/horizon/` | block / item / entity_type / creative_tab declarations |
| `content/data/deeperdarker/{loot_table,recipe,tags}/` | loot, recipes, tags in 26.3 shape |
| `mixins/deeperdarker/horizon-mixin.toml` | native bundle manifest, pinned revision |
| `mixins/deeperdarker/api/` | the native crate (`mod-deeperdarker`) |
| `tools/port.py` | rebuilds `content/` from the unpacked upstream 1.21.1 jar |
| `tools/pack.py` | builds `target/deeperdarker.hmod` and `target/deeperdarker.hnmod` |
| `tools/vps_sync.sh`, `tools/vps_stage.sh`, `tools/check.sh` | VPS build/test harness |
| `LICENSE` | upstream GPL-3.0 text, unchanged |
| `NOTICE.md` | what was copied and what was changed, per GPL-3.0 §5a |

## Done

- **Blocks — 127** declared on vanilla templates (`data/deeperdarker/horizon/block/`),
  with upstream's blockstates, models and textures: sculk stone and its
  polished/cut/brick/grime/gleam variants, gloomslate and its brick/tile/ore
  variants, echo wood (log, planks, stairs, slabs, fences, doors, trapdoors,
  signs, hanging signs), bloom wood and blooming stem/moss, infested sculk,
  lite/bordered lite block, crystallized amber, sculk transmitters and the
  rest of what upstream registers. Slabs, stairs, walls, fences, gates,
  buttons, pressure plates, doors and trapdoors use the matching vanilla
  templates and state sets.
- **Items — 41** (`horizon/item/`): the mod's materials, tools and armour,
  with upstream durability, attack damage/speed, armour, toughness and
  knockback resistance as 26.3 components; equipment assets for the two armour
  materials re-pathed to 26.3's `textures/entity/equipment/humanoid*/`.
- **Mobs — 7** (`horizon/entity_type/`): sculk centipede, sculk leech, shriek
  worm, shattered, anger/fear/sorrow overcast pot. Living types on the zombie
  template with upstream attributes and hitbox sizes where the template
  allows; spawns in the vanilla deep dark (see Missing).
- **Loot — 128 tables**, rewritten in 26.3 shape: every ported block drops
  itself, the seven mobs drop upstream's items.
- **Recipes — 241**, 26.3 shape; smithing recipes keep upstream's template,
  base and addition.
- **Sounds** (`sounds.json` + 81 `.ogg`) and **all 31 upstream language
  files**.
- **Tags** for the ids this port registers, including the vanilla
  `minecraft:tags/block/mineable/*` entries.
- **Native half** (497 lines of Rust, original code): `register_goals` for the
  seven kinds, the shriek worm's emerge (80 ticks) / idle (1200) / dig (83)
  cycle ending in infested sculk and the mob's removal, the shattered's
  16-block vibration hearing driven by `game_event`, the drowned-conversion
  guard for this mod's kinds, and world-open/close state reset.
- **Packaging**: `.hmod` and `.hnmod` build reproducibly with `tools/pack.py`;
  LICENSE and NOTICE travel inside both files.

## Missing

- **The Otherside dimension.** Horizon content mods cannot add a dimension, so
  the portal block, its portal logic, the Otherside biomes, noise settings,
  carvers, features and structures are not ported. The mobs spawn in the
  vanilla deep dark instead, and the portal frame/ignition gameplay is absent.
- **The Stalker boss** and its fight, music and loot.
- **Boat and chest boat** entities (`deeperdarker:boat`, chest boat).
- **Custom painting**, advancements, and the `sculk_transmitter_coloring`
  recipe type.
- **Mob behaviour beyond the listed goals**: upstream's neutral-anger system
  for the sculk centipede, the shriek worm's sonic attack shape, the pots'
  spawn/possession mechanics, and mob-specific sounds/particles.
- **Tool-predicate loot**: upstream's cobbled-stone-without-silk-touch tables
  are flattened to self-drop. Enchantment-sensitive drops are not translated.
- **Mob rendering**: textures are shipped but nothing draws the mobs yet (the
  game has no renderer for these custom kinds in this build).
- **Structures/worldgen**: the ancient-city-adjacent Otherside content and any
  upstream worldgen JSON are not ported (dimension absent).
- No dedicated-server smoke run with the mod loaded was performed in this
  session; verification is compile-, test- and package-level (see below).

## Build and test

Content and packaging are light and run anywhere:

```sh
python tools/port.py <unpacked upstream 1.21.1 jar assets+data dir>   # optional: regenerate content
python tools/pack.py                                                  # target/*.hmod, *.hnmod
```

Native code builds on the VPS (never a full game build locally):

```sh
sh tools/vps_sync.sh                  # copy the mod to /opt/build/mods/deeperdarker
ssh ... 'bash /opt/build/mods/deeperdarker/tools/vps_stage.sh'
ssh ... 'bash /opt/build/mods/deeperdarker/tools/check.sh full'
```

`tools/vps_stage.sh` creates the worktree `/opt/build/wt/deeperdarker` at the
pinned revision and stages `mixins/deeperdarker/api` as the launcher does, so
the checks build the native crate against the real game sources.

Last results (2026-11-13):

| Check | Result |
| --- | --- |
| `cargo check -p mod-deeperdarker` (server flavour) | pass |
| `cargo test -p mod-deeperdarker` | 4 passed, 0 failed |
| `cargo check -p horizon-native-game` (client flavour, default features) | pass |
| `cargo horizon-mod check deeperdarker.hmod` | pass (API 0.2, content only) |
| `cargo horizon-mod check deeperdarker.hnmod` | pass (native-1, pinned revision) |

## Licensing

Upstream is **GPL-3.0-only**; this port is distributed under the same licence
and keeps upstream's `LICENSE` unchanged. `NOTICE.md` records exactly which
assets and data are copied from upstream, which files changed and how, and
which parts are original work. The port's own scripts and Rust
(`tools/*.py`, `mixins/deeperdarker/api/src/`) are original, GPL-3.0, by the
Saison 2 server.

Copyright (C) 2022–2026 Kyanite Mods for upstream code, textures, models,
sounds, data and names.
Copyright (C) 2026 the Saison 2 server for the Horizon port.
