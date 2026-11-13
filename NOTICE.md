# NOTICE

This mod is a Horizon port of **Deeper and Darker** by **Kyanite Mods**.

- Upstream: https://github.com/KyaniteMods/DeeperAndDarker
- Branch `neoforge-26.1` (Minecraft 26.1.2, version 1.4.1) for the Java
  behaviour this port follows, and the published 1.21.1 NeoForge jar
  `deeperdarker-neoforge-1.21.1-1.4.1.jar` (Modrinth project `deeperdarker`,
  version `1.4.1-neoforge-1.21.1`, SHA-256 of the jar in the build notes) for
  the blocks', items' and mobs' assets and data, which the 26.1 branch keeps in
  datagen rather than in `src/main/resources`.
- Licence: GNU General Public License v3.0 only (`LICENSE`, copied unchanged
  from upstream's `LICENSE`). This port is distributed under the same licence.

Copyright (C) 2022–2026 Kyanite Mods, for the upstream code, textures, models,
sounds, data and names.
Copyright (C) 2026 the Saison 2 server, for the changes listed below.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, version 3. It is distributed WITHOUT ANY WARRANTY; see `LICENSE`.

## What is copied from upstream, unchanged

Copied by `tools/port.py` from the jar above (paths kept under
`content/assets/deeperdarker/` and `content/data/deeperdarker/`):

- block models, blockstates and textures of the ported blocks, item models and
  item textures of the ported items, and the textures of the ported mobs
  (kept for a later client slice; nothing draws them yet);
- upstream's armour layers (`textures/models/armor/*.png`), re-pathed to 26.3's
  `textures/entity/equipment/humanoid/` and `humanoid_leggings/`;
- the sound events (`sounds.json`) and their `.ogg` files, and every language
  file in `lang/`;
- the 1.21.1 recipes that only name items this port registers or vanilla items,
  converted to 26.3's recipe shape by the script;
- upstream's item and block tags that name ids this port registers.

## What is changed (GPL-3.0 section 5a)

All changes were made in November 2026 for Horizon by the Saison 2 server.

- **Blocks** (`data/deeperdarker/horizon/block/`): 127 blocks declared on
  vanilla templates chosen from the vanilla block each upstream block copies
  (`Properties.ofFullCopy`), with upstream's state set. Signs and hanging signs
  are declared as signs with their wall forms; the blooming stem is a
  `chorus_plant` copy with `connects_to` and its 26 age values.
- **Items** (`data/deeperdarker/horizon/item/`): 41 items on vanilla templates.
  Tools and armour carry upstream's durability, attack damage and attack speed,
  armour, toughness and knockback resistance as 26.3 components; the two
  armour materials get 26.3 equipment assets from upstream's 1.21.1 layers.
- **Mobs** (`data/deeperdarker/horizon/entity_type/`): the sculk centipede,
  sculk leech, shriek worm, shattered and the three overcast pots as living
  types on the zombie template with upstream's attributes, hitbox sizes except
  the template's, and the deep dark as their spawn biome (see README.md).
  Their loot tables are rewritten in 26.3's shape from upstream's drops.
- **Loot**: every ported block drops itself; upstream's tool-predicate tables
  (cobbled stone without silk touch) are not translated.
- **Native half** (`mixins/deeperdarker/`): original Rust written against
  Horizon's mod API from upstream's documented behaviour and its Java goals
  (`content/entities/*.java`, read as a licence-permitted reference): the
  goals of the seven mobs, the shriek worm's emerge/idle/dig cycle, the
  shattered's vibration listening and the drowned-conversion guard.
- **Recipes**: 26.3 shape; smithing transforms keep upstream's template, base
  and addition, with the templates as plain items.
- **Not copied**: the Otherside dimension, its biomes, noise settings,
  carvers, features, structures and portal block, the Stalker boss, the
  boat/chest boat entities, the custom painting, advancements, the
  `sculk_transmitter_coloring` recipe type, and every Java class.

The port's own code and scripts (`tools/*.py`, `mixins/deeperdarker/api/src/`)
are original work, GPL-3.0, by the Saison 2 server.
