#!/usr/bin/env python3
"""Build content/ (the .hmod tree) from Deeper and Darker's upstream files.

Part of the Horizon port of Deeper and Darker by Kyanite Mods (GPL-3.0; see
LICENSE and NOTICE.md in the mod folder). Changed for Horizon by the Saison 2
server; NOTICE.md lists what was copied and what was changed.

    python -I tools/port.py <upstream resources dir>

`<upstream resources dir>` is the `assets/` + `data/` tree of the upstream
1.21.1 jar (deeperdarker-neoforge-1.21.1-1.4.1.jar, unpacked; see NOTICE.md
for the download address and version). The script copies the GPL assets and
data this slice uses and writes the Horizon declarations next to them:

- blocks on vanilla templates (data/deeperdarker/horizon/block/), with their
  items, models, 26.3 item definitions, self-drop loot and a creative tab;
- items of the mod's own (materials, tools, armour) on vanilla templates with
  the upstream durability, armour values and attack numbers as components,
  and 26.3 equipment assets for the two armour materials;
- the seven mobs of this slice (sculk centipede, sculk leech, shriek worm,
  shattered, the three overcast pots) as living entity types on the zombie
  template, with upstream's attributes, loot and deep dark spawns.

Everything under content/ is rewritten on each run, so the result only
depends on the upstream tree and this file. The Otherside dimension, its
biomes and structures are not generated: Horizon content mods cannot add a
dimension (docs/modpacks.md, "Dimensions"), so the mobs live in the vanilla
deep dark instead.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONTENT = os.path.join(ROOT, "content")
NS = "deeperdarker"

# --------------------------------------------------------------------------
# Blocks: upstream name -> vanilla template. Upstream builds almost every
# block with `Properties.ofFullCopy(<vanilla block>)`, and the template's
# states are exactly the blockstate file's properties, so the template is the
# block whose class and states upstream copied.
# --------------------------------------------------------------------------
BLOCKS = {
    # Sculk stone, and every cut of it.
    "sculk_stone": "minecraft:stone",
    "sculk_stone_stairs": "minecraft:stone_stairs",
    "sculk_stone_slab": "minecraft:stone_slab",
    "sculk_stone_wall": "minecraft:cobblestone_wall",
    "cobbled_sculk_stone": "minecraft:cobblestone",
    "cobbled_sculk_stone_stairs": "minecraft:cobblestone_stairs",
    "cobbled_sculk_stone_slab": "minecraft:cobblestone_slab",
    "cobbled_sculk_stone_wall": "minecraft:cobblestone_wall",
    "polished_sculk_stone": "minecraft:polished_andesite",
    "polished_sculk_stone_stairs": "minecraft:stone_stairs",
    "polished_sculk_stone_slab": "minecraft:stone_slab",
    "polished_sculk_stone_wall": "minecraft:cobblestone_wall",
    "sculk_stone_bricks": "minecraft:stone_bricks",
    "sculk_stone_brick_stairs": "minecraft:stone_brick_stairs",
    "sculk_stone_brick_slab": "minecraft:stone_brick_slab",
    "sculk_stone_brick_wall": "minecraft:stone_brick_wall",
    "sculk_stone_tiles": "minecraft:deepslate_tiles",
    "sculk_stone_tile_stairs": "minecraft:deepslate_tile_stairs",
    "sculk_stone_tile_slab": "minecraft:deepslate_tile_slab",
    "sculk_stone_tile_wall": "minecraft:deepslate_tile_wall",
    "smooth_sculk_stone": "minecraft:smooth_stone",
    "smooth_sculk_stone_stairs": "minecraft:stone_stairs",
    "smooth_sculk_stone_slab": "minecraft:smooth_stone_slab",
    "smooth_sculk_stone_wall": "minecraft:cobblestone_wall",
    "cut_sculk_stone": "minecraft:stone",
    "cut_sculk_stone_stairs": "minecraft:stone_stairs",
    "cut_sculk_stone_slab": "minecraft:stone_slab",
    "cut_sculk_stone_wall": "minecraft:cobblestone_wall",
    "chiseled_sculk_stone": "minecraft:chiseled_stone_bricks",
    "blooming_sculk_stone": "minecraft:stone",
    "sculk_grime": "minecraft:mud",
    "sculk_grime_bricks": "minecraft:stone_bricks",
    "sculk_grime_brick_slab": "minecraft:stone_brick_slab",
    "sculk_grime_brick_stairs": "minecraft:stone_brick_stairs",
    "sculk_grime_brick_wall": "minecraft:stone_brick_wall",
    # Gloomslate, the deepslate of the Otherside.
    "gloomslate": "minecraft:deepslate",
    "gloomslate_stairs": "minecraft:cobbled_deepslate_stairs",
    "gloomslate_slab": "minecraft:cobbled_deepslate_slab",
    "gloomslate_wall": "minecraft:cobbled_deepslate_wall",
    "cobbled_gloomslate": "minecraft:cobbled_deepslate",
    "cobbled_gloomslate_stairs": "minecraft:cobbled_deepslate_stairs",
    "cobbled_gloomslate_slab": "minecraft:cobbled_deepslate_slab",
    "cobbled_gloomslate_wall": "minecraft:cobbled_deepslate_wall",
    "polished_gloomslate": "minecraft:polished_deepslate",
    "polished_gloomslate_stairs": "minecraft:polished_deepslate_stairs",
    "polished_gloomslate_slab": "minecraft:polished_deepslate_slab",
    "polished_gloomslate_wall": "minecraft:polished_deepslate_wall",
    "gloomslate_bricks": "minecraft:deepslate_bricks",
    "gloomslate_brick_stairs": "minecraft:deepslate_brick_stairs",
    "gloomslate_brick_slab": "minecraft:deepslate_brick_slab",
    "gloomslate_brick_wall": "minecraft:deepslate_brick_wall",
    "gloomslate_brick_fence": "minecraft:nether_brick_fence",
    "gloomslate_tiles": "minecraft:deepslate_tiles",
    "gloomslate_tile_stairs": "minecraft:deepslate_tile_stairs",
    "gloomslate_tile_slab": "minecraft:deepslate_tile_slab",
    "gloomslate_tile_wall": "minecraft:deepslate_tile_wall",
    "smooth_gloomslate": "minecraft:polished_deepslate",
    "smooth_gloomslate_stairs": "minecraft:cobbled_deepslate_stairs",
    "smooth_gloomslate_slab": "minecraft:polished_deepslate_slab",
    "smooth_gloomslate_wall": "minecraft:cobbled_deepslate_wall",
    "cut_gloomslate": "minecraft:deepslate",
    "cut_gloomslate_stairs": "minecraft:cobbled_deepslate_stairs",
    "cut_gloomslate_slab": "minecraft:deepslate_tile_slab",
    "cut_gloomslate_wall": "minecraft:cobbled_deepslate_wall",
    "chiseled_gloomslate": "minecraft:chiseled_deepslate",
    "enriched_gloomslate_bricks": "minecraft:deepslate_bricks",
    # Ores.
    "sculk_stone_coal_ore": "minecraft:coal_ore",
    "sculk_stone_iron_ore": "minecraft:iron_ore",
    "sculk_stone_copper_ore": "minecraft:copper_ore",
    "sculk_stone_gold_ore": "minecraft:gold_ore",
    "sculk_stone_redstone_ore": "minecraft:redstone_ore",
    "sculk_stone_emerald_ore": "minecraft:emerald_ore",
    "sculk_stone_lapis_ore": "minecraft:lapis_ore",
    "sculk_stone_diamond_ore": "minecraft:diamond_ore",
    "gloomslate_coal_ore": "minecraft:deepslate_coal_ore",
    "gloomslate_iron_ore": "minecraft:deepslate_iron_ore",
    "gloomslate_copper_ore": "minecraft:deepslate_copper_ore",
    "gloomslate_gold_ore": "minecraft:deepslate_gold_ore",
    "gloomslate_redstone_ore": "minecraft:deepslate_redstone_ore",
    "gloomslate_emerald_ore": "minecraft:deepslate_emerald_ore",
    "gloomslate_lapis_ore": "minecraft:deepslate_lapis_ore",
    "gloomslate_diamond_ore": "minecraft:deepslate_diamond_ore",
    # Echo wood.
    "echo_log": "minecraft:oak_log",
    "echo_wood": "minecraft:oak_wood",
    "stripped_echo_log": "minecraft:stripped_oak_log",
    "stripped_echo_wood": "minecraft:stripped_oak_wood",
    "echo_planks": "minecraft:oak_planks",
    "echo_stairs": "minecraft:oak_stairs",
    "echo_slab": "minecraft:oak_slab",
    "echo_fence": "minecraft:oak_fence",
    "echo_fence_gate": "minecraft:oak_fence_gate",
    "echo_door": "minecraft:oak_door",
    "echo_trapdoor": "minecraft:oak_trapdoor",
    "echo_button": "minecraft:oak_button",
    "echo_pressure_plate": "minecraft:oak_pressure_plate",
    "echo_leaves": "minecraft:oak_leaves",
    "echo_sapling": "minecraft:oak_sapling",
    "echo_soil": "minecraft:moss_block",
    # Bloom wood.
    "bloom_planks": "minecraft:oak_planks",
    "bloom_stairs": "minecraft:oak_stairs",
    "bloom_slab": "minecraft:oak_slab",
    "bloom_fence": "minecraft:oak_fence",
    "bloom_fence_gate": "minecraft:oak_fence_gate",
    "bloom_door": "minecraft:oak_door",
    "bloom_trapdoor": "minecraft:oak_trapdoor",
    "bloom_button": "minecraft:oak_button",
    "bloom_pressure_plate": "minecraft:oak_pressure_plate",
    # Lighting, glass and the small decorative blocks.
    "sculk_gleam": "minecraft:sculk",
    "gloomslate_light": "minecraft:glowstone",
    "lite_block": "minecraft:verdant_froglight",
    "bordered_lite_block": "minecraft:sea_lantern",
    "soundproof_glass": "minecraft:glass",
    "crystallized_amber": "minecraft:glass",
    "infested_sculk": "minecraft:sculk",
    "blooming_moss_block": "minecraft:moss_block",

}

# Blocks that need more than a template: signs (their wall form is what the
# item places) and the blooming stem (six connections and an age property).
SPECIAL = {
    "potted_echo_sapling": {"template": "minecraft:potted_oak_sapling", "item": False},
    "potted_blooming_stem": {"template": "minecraft:potted_oak_sapling", "item": False},
    "echo_sign": {
        "template": "minecraft:oak_sign",
        "wall_block": NS + ":echo_wall_sign",
        "components": {"minecraft:max_stack_size": 16},
    },
    "echo_wall_sign": {"template": "minecraft:oak_wall_sign", "item": False},
    "echo_hanging_sign": {
        "template": "minecraft:oak_hanging_sign",
        "wall_block": NS + ":echo_wall_hanging_sign",
        "components": {"minecraft:max_stack_size": 16},
    },
    "echo_wall_hanging_sign": {
        "template": "minecraft:oak_wall_hanging_sign",
        "item": False,
    },
    "bloom_sign": {
        "template": "minecraft:oak_sign",
        "wall_block": NS + ":bloom_wall_sign",
        "components": {"minecraft:max_stack_size": 16},
    },
    "bloom_wall_sign": {"template": "minecraft:oak_wall_sign", "item": False},
    "bloom_hanging_sign": {
        "template": "minecraft:oak_hanging_sign",
        "wall_block": NS + ":bloom_wall_hanging_sign",
        "components": {"minecraft:max_stack_size": 16},
    },
    "bloom_wall_hanging_sign": {
        "template": "minecraft:oak_wall_hanging_sign",
        "item": False,
    },
    "blooming_stem": {
        "template": "minecraft:chorus_plant",
        "connects_to": "#" + NS + ":bloom_stem_connects",
        "thickness": 6,
        "state_properties": {
            "age": {"type": "enum", "values": [str(i) for i in range(26)]}
        },
        "default_state": {"age": "0"},
    },
    "stripped_blooming_stem": {
        "template": "minecraft:chorus_plant",
        "connects_to": "#" + NS + ":bloom_stem_connects",
        "thickness": 6,
        "state_properties": {
            "age": {"type": "enum", "values": [str(i) for i in range(26)]}
        },
        "default_state": {"age": "0"},
    },
}

# Blocks that are cut from another block upstream: the stonecutter recipes
# follow from these pairs.
CUT_FROM = {
    "sculk_stone": [
        "sculk_stone_stairs", "sculk_stone_slab", "sculk_stone_wall",
        "cobbled_sculk_stone", "polished_sculk_stone", "sculk_stone_bricks",
        "sculk_stone_tiles", "smooth_sculk_stone", "cut_sculk_stone",
        "chiseled_sculk_stone",
    ],
    "gloomslate": [
        "gloomslate_stairs", "gloomslate_slab", "gloomslate_wall",
        "cobbled_gloomslate", "polished_gloomslate", "gloomslate_bricks",
        "gloomslate_tiles", "smooth_gloomslate", "cut_gloomslate",
        "chiseled_gloomslate", "gloomslate_brick_fence",
    ],
    "sculk_grime": ["sculk_grime_bricks"],
    "echo_planks": [
        "echo_stairs", "echo_slab", "echo_fence", "echo_fence_gate",
    ],
    "bloom_planks": [
        "bloom_stairs", "bloom_slab", "bloom_fence", "bloom_fence_gate",
    ],
}

# --------------------------------------------------------------------------
# Items of the mod's own (not block items). `template` is a vanilla item of
# the same class; the components carry upstream's numbers.
# --------------------------------------------------------------------------
TOOL_MATERIALS = {
    "resonarium": {
        "max_damage": 1601,
        "enchantable": 11,
        "attack": {"sword": 8.0, "axe": 9.0, "pickaxe": 6.0, "shovel": 5.5, "hoe": 4.0},
        "speed": {"sword": -2.4, "axe": -3.0, "pickaxe": -2.8, "shovel": -3.0, "hoe": 0.0},
        "rarity": None,
        "fire_resistant": False,
    },
    "warden": {
        "max_damage": 2519,
        "enchantable": 18,
        "attack": {"sword": 10.0, "axe": 12.0, "pickaxe": 8.0, "shovel": 7.0, "hoe": 5.0},
        "speed": {"sword": -2.4, "axe": -3.0, "pickaxe": -2.8, "shovel": -3.0, "hoe": 0.0},
        "rarity": "rare",
        "fire_resistant": True,
    },
}

# durability multiplier -> the four armour pieces (upstream ArmorType).
ARMOR_MATERIALS = {
    "resonarium": {
        "durability": {"helmet": 330, "chestplate": 480, "leggings": 450, "boots": 390},
        "defense": {"helmet": 3, "chestplate": 8, "leggings": 6, "boots": 3},
        "toughness": 2.0,
        "knockback_resistance": 0.0,
        "enchantable": 10,
        "equip_sound": "minecraft:item.armor.equip_diamond",
        "rarity": None,
        "fire_resistant": False,
    },
    "warden": {
        "durability": {"helmet": 440, "chestplate": 640, "leggings": 600, "boots": 520},
        "defense": {"helmet": 4, "chestplate": 9, "leggings": 7, "boots": 4},
        "toughness": 4.0,
        "knockback_resistance": 0.1,
        "enchantable": 18,
        "equip_sound": "minecraft:item.armor.equip_netherite",
        "rarity": "rare",
        "fire_resistant": True,
    },
}

ITEMS = {
    # Materials. Upstream registers them with no behaviour of their own.
    "sculk_bone": {},
    "grime_ball": {},
    "grime_brick": {},
    "gleam_gel": {},
    "lite": {},
    "soul_dust": {},
    "soul_crystal": {},
    "resonarium": {},
    "resonarium_plate": {},
    "gloomsherd": {},
    "brittle_gloomsherd": {},
    "dark_heart_gloomsherd": {},
    "listener_gloomsherd": {},
    "snapper_gloomsherd": {},
    "temple_gloomsherd": {},
    "transmission_gloomsherd": {},
    "ward_gloomsherd": {},
    "wayfinder_gloomsherd": {},
    "heart_of_the_deep": {
        "rarity": "rare",
        "max_stack_size": 1,
        "components": {"minecraft:damage_resistant": {"types": "#minecraft:is_fire"}},
    },
    "warden_carapace": {
        "rarity": "rare",
        "components": {"minecraft:damage_resistant": {"types": "#minecraft:is_fire"}},
    },
    "reinforced_echo_shard": {
        "rarity": "rare",
        "components": {"minecraft:damage_resistant": {"types": "#minecraft:is_fire"}},
    },
    # The smithing templates are plain items here: their recipes are the two
    # transforms below, and a template's own tooltip is not ported.
    "resonarium_upgrade_smithing_template": {"rarity": "uncommon"},
    "warden_upgrade_smithing_template": {"rarity": "uncommon"},
}

# --------------------------------------------------------------------------
# Mobs of this slice: upstream mob -> (attributes, loot). The living type
# copies the zombie, a Monster, and the native half (`mixins/deeperdarker`)
# replaces its goals and adds the mob's own behaviour.
# --------------------------------------------------------------------------
MOBS = {
    "sculk_centipede": {
        "attributes": {
            "minecraft:max_health": 20.0,
            "minecraft:attack_damage": 3.0,
            "minecraft:movement_speed": 0.2,
            "minecraft:spawn_reinforcements": 0.0,
        },
        "loot": [("minecraft:string", 0, 1)],
        "spawn": (6, 1, 4),
    },
    "sculk_leech": {
        "attributes": {
            "minecraft:max_health": 4.0,
            "minecraft:attack_damage": 1.0,
            "minecraft:movement_speed": 0.25,
            "minecraft:spawn_reinforcements": 0.0,
        },
        "loot": [(NS + ":soul_dust", 0, 1)],
        # Upstream lets the Stalker spawn these; the deep dark gets a few so
        # the port has them in play without the boss.
        "spawn": (4, 1, 2),
    },
    "shriek_worm": {
        "attributes": {
            "minecraft:max_health": 100.0,
            "minecraft:attack_damage": 7.0,
            "minecraft:movement_speed": 0.0,
            "minecraft:attack_knockback": 0.0,
            "minecraft:knockback_resistance": 1.0,
            "minecraft:spawn_reinforcements": 0.0,
        },
        "loot": [],
        "spawn": None,
    },
    "shattered": {
        "attributes": {
            "minecraft:max_health": 50.0,
            "minecraft:attack_damage": 6.0,
            "minecraft:movement_speed": 0.2,
            "minecraft:armor": 3.5,
            "minecraft:follow_range": 10.0,
            "minecraft:spawn_reinforcements": 0.0,
        },
        "loot": [(NS + ":sculk_bone", 1, 3)],
        "spawn": (5, 2, 4),
    },
    "anger_pot": {
        "attributes": {
            "minecraft:max_health": 40.0,
            "minecraft:attack_damage": 5.0,
            "minecraft:movement_speed": 0.3,
            "minecraft:spawn_reinforcements": 0.0,
        },
        "loot": [
            (NS + ":gloomsherd", 1, 1),
        ],
        "spawn": None,
    },
    "fear_pot": {
        "attributes": {
            "minecraft:max_health": 30.0,
            "minecraft:attack_damage": 5.0,
            "minecraft:movement_speed": 0.3,
            "minecraft:spawn_reinforcements": 0.0,
        },
        "loot": [
            (NS + ":gloomsherd", 1, 1),
        ],
        "spawn": None,
    },
    "sorrow_pot": {
        "attributes": {
            "minecraft:max_health": 20.0,
            "minecraft:attack_damage": 5.0,
            "minecraft:movement_speed": 0.3,
            "minecraft:spawn_reinforcements": 0.0,
        },
        "loot": [
            (NS + ":gloomsherd", 1, 1),
        ],
        "spawn": None,
    },
}

# Blocks that only the wood families put in an axe/shovel tag.
AXE_BLOCKS = [n for n in BLOCKS if n.startswith(("echo_", "bloom_")) and not n.startswith("echo_soil")]
SHOVEL_BLOCKS = ["echo_soil", "sculk_grime", "blooming_moss_block"]
STONE_TOOL_BLOCKS = [
    n for n in BLOCKS
    if n.startswith(("sculk_stone", "cobbled_sculk", "polished_sculk", "smooth_sculk",
                     "cut_sculk", "chiseled_sculk", "blooming_sculk", "gloomslate",
                     "cobbled_gl", "polished_gl", "smooth_gl", "cut_gl", "chiseled_gl",
                     "enriched_gl", "sculk_grime"))
]
IRON_TOOL_BLOCKS = [n for n in BLOCKS if n.endswith(("_diamond_ore", "_emerald_ore", "_gold_ore", "_redstone_ore"))]


def die(msg):
    raise SystemExit("port.py: " + msg)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
        f.write("\n")


def copy(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copyfile(src, dst)


def clean():
    if os.path.isdir(CONTENT):
        shutil.rmtree(CONTENT)
    for path in ("assets", "data"):
        os.makedirs(os.path.join(CONTENT, path), exist_ok=True)


def block_item_names():
    names = []
    for name, spec in list(BLOCKS.items()) + [(n, s) for n, s in SPECIAL.items()]:
        if isinstance(spec, str) or spec.get("item", True):
            names.append(name)
    return names


def copy_assets(up):
    src = os.path.join(up, "assets", NS)
    dst = os.path.join(CONTENT, "assets", NS)
    # Models, blockstates and textures: the ported blocks and items use them,
    # and the blockstates of a template are what its states look like.
    for folder in ("models", "textures"):
        shutil.copytree(os.path.join(src, folder), os.path.join(dst, folder))
    os.makedirs(os.path.join(dst, "blockstates"), exist_ok=True)
    for name in list(BLOCKS) + list(SPECIAL):
        path = os.path.join(src, "blockstates", name + ".json")
        if os.path.exists(path):
            copy(path, os.path.join(dst, "blockstates", name + ".json"))
    for name in ("blooming_stem", "stripped_blooming_stem"):
        copy(
            os.path.join(src, "blockstates", name + ".json"),
            os.path.join(dst, "blockstates", name + ".json"),
        )
    # Sounds: all of upstream's events and files (the native half plays the
    # mobs' sounds; blocks keep their template's).
    shutil.copytree(os.path.join(src, "sounds"), os.path.join(dst, "sounds"))
    copy(os.path.join(src, "sounds.json"), os.path.join(dst, "sounds.json"))
    # Names, in every language upstream ships. The jar also carries the same
    # files without the `.json` suffix; keep the plain `xx_yy.json` names.
    os.makedirs(os.path.join(dst, "lang"), exist_ok=True)
    for name in sorted(os.listdir(os.path.join(src, "lang"))):
        if name.endswith(".json"):
            copy(os.path.join(src, "lang", name), os.path.join(dst, "lang", name))


def write_item_definitions():
    """26.3 item definitions: every item's model, from the 1.21.1 model."""
    models = os.path.join(CONTENT, "assets", NS, "models", "item")
    out = os.path.join(CONTENT, "assets", NS, "items")
    missing = []
    for name in block_item_names() + list(ITEMS) + tool_item_names() + armor_item_names():
        model = os.path.join(models, name + ".json")
        if not os.path.exists(model):
            missing.append(name)
            continue
        write_json(os.path.join(out, name + ".json"), {
            "model": {"type": "minecraft:model", "model": f"{NS}:item/{name}"},
        })
    if missing:
        die("no item model for: " + ", ".join(missing))


def tool_item_names():
    return [f"{mat}_{kind}" for mat in TOOL_MATERIALS for kind in ("sword", "axe", "pickaxe", "shovel", "hoe")]


def armor_item_names():
    return [f"{mat}_{piece}" for mat in ARMOR_MATERIALS for piece in ("helmet", "chestplate", "leggings", "boots")]


def write_blocks():
    for name in BLOCKS:
        write_json(os.path.join(CONTENT, "data", NS, "horizon", "block", name + ".json"), {
            "template": BLOCKS[name],
            "item": True,
        })
    for name, spec in SPECIAL.items():
        decl = dict(spec)
        decl.setdefault("item", True)
        write_json(os.path.join(CONTENT, "data", NS, "horizon", "block", name + ".json"), decl)


def write_items():
    for name, spec in ITEMS.items():
        # A plain item sets `max_stack_size` and `rarity` as keys of its own;
        # a block's item (below) has only the `components` form.
        decl = {"template": "minecraft:stick"}
        for key in ("components", "rarity", "max_stack_size"):
            if key in spec:
                decl[key] = spec[key]
        write_json(os.path.join(CONTENT, "data", NS, "horizon", "item", name + ".json"), decl)

    for mat, m in TOOL_MATERIALS.items():
        for kind in ("sword", "axe", "pickaxe", "shovel", "hoe"):
            decl = {
                "template": f"minecraft:iron_{kind}",
                "components": {
                    "minecraft:max_damage": m["max_damage"],
                    "minecraft:enchantable": {"value": m["enchantable"]},
                    "minecraft:attribute_modifiers": [
                        {
                            "type": "minecraft:attack_damage",
                            "id": "minecraft:base_attack_damage",
                            "amount": m["attack"][kind],
                            "operation": "add_value",
                            "slot": "mainhand",
                        },
                        {
                            "type": "minecraft:attack_speed",
                            "id": "minecraft:base_attack_speed",
                            "amount": m["speed"][kind],
                            "operation": "add_value",
                            "slot": "mainhand",
                        },
                    ],
                },
            }
            if m["rarity"]:
                decl["rarity"] = m["rarity"]
            if m["fire_resistant"]:
                decl["components"]["minecraft:damage_resistant"] = {"types": "#minecraft:is_fire"}
            write_json(os.path.join(CONTENT, "data", NS, "horizon", "item", f"{mat}_{kind}.json"), decl)

    for mat, m in ARMOR_MATERIALS.items():
        for piece, slot in (("helmet", "head"), ("chestplate", "chest"),
                            ("leggings", "legs"), ("boots", "feet")):
            mods = [
                {
                    "type": "minecraft:armor",
                    "id": f"{NS}:armor.{piece}",
                    "amount": float(m["defense"][piece]),
                    "operation": "add_value",
                    "slot": slot,
                },
                {
                    "type": "minecraft:armor_toughness",
                    "id": f"{NS}:armor.{piece}",
                    "amount": m["toughness"],
                    "operation": "add_value",
                    "slot": slot,
                },
            ]
            if m["knockback_resistance"] > 0:
                mods.append({
                    "type": "minecraft:knockback_resistance",
                    "id": f"{NS}:armor.{piece}",
                    "amount": m["knockback_resistance"],
                    "operation": "add_value",
                    "slot": slot,
                })
            # Upstream's WardenArmorItem adds its speed bonus to the leggings.
            if piece == "leggings" and m["knockback_resistance"] > 0:
                mods.append({
                    "type": "minecraft:movement_speed",
                    "id": f"{NS}:armor.{piece}",
                    "amount": 0.05,
                    "operation": "add_value",
                    "slot": slot,
                })
            decl = {
                "template": f"minecraft:iron_{piece}",
                "components": {
                    "minecraft:max_damage": m["durability"][piece],
                    "minecraft:enchantable": {"value": m["enchantable"]},
                    "minecraft:attribute_modifiers": mods,
                    "minecraft:equippable": {
                        "slot": slot,
                        "asset_id": f"{NS}:{mat}",
                        "equip_sound": m["equip_sound"],
                    },
                },
            }
            if m["rarity"]:
                decl["rarity"] = m["rarity"]
            if m["fire_resistant"]:
                decl["components"]["minecraft:damage_resistant"] = {"types": "#minecraft:is_fire"}
            write_json(os.path.join(CONTENT, "data", NS, "horizon", "item", f"{mat}_{piece}.json"), decl)


def write_equipment(up):
    """26.3 equipment assets from upstream's 1.21.1 armour layers."""
    src = os.path.join(up, "assets", NS, "textures", "models", "armor")
    dst = os.path.join(CONTENT, "assets", NS, "textures", "entity", "equipment")
    for mat in ARMOR_MATERIALS:
        for layer, kind in ((1, "humanoid"), (2, "humanoid_leggings")):
            copy(
                os.path.join(src, f"{mat}_layer_{layer}.png"),
                os.path.join(dst, kind, mat + ".png"),
            )
        write_json(os.path.join(CONTENT, "assets", NS, "equipment", mat + ".json"), {
            "layers": {
                "humanoid": [{"texture": f"{NS}:{mat}"}],
                "humanoid_leggings": [{"texture": f"{NS}:{mat}"}],
            },
        })


def write_entity_types():
    for name, mob in MOBS.items():
        write_json(os.path.join(CONTENT, "data", NS, "horizon", "entity_type", name + ".json"), {
            "template": "minecraft:zombie",
            "attributes": mob["attributes"],
        })
        pools = []
        if mob["loot"]:
            entries = []
            for item, lo, hi in mob["loot"]:
                entry = {"type": "minecraft:item", "name": item}
                if lo != hi:
                    entry["modifier"] = [{
                        "type": "minecraft:set_count",
                        "count": {"type": "minecraft:uniform", "min": lo, "max": hi},
                        "add": False,
                    }]
                elif lo != 1:
                    entry["modifier"] = [{
                        "type": "minecraft:set_count",
                        "count": lo,
                        "add": False,
                    }]
                entries.append(entry)
            pools.append({"rolls": 1, "bonus_rolls": 0, "entries": entries})
        write_json(os.path.join(CONTENT, "data", NS, "loot_table", "entities", name + ".json"), {
            "type": "minecraft:entity",
            "pools": pools,
            "random_sequence": f"{NS}:entities/{name}",
        })

    spawners = [
        {"type": f"{NS}:{name}", "weight": mob["spawn"][0],
         "minCount": mob["spawn"][1], "maxCount": mob["spawn"][2]}
        for name, mob in MOBS.items() if mob["spawn"]
    ]
    write_json(os.path.join(CONTENT, "data", NS, "neoforge", "biome_modifier", "add_deep_dark_spawns.json"), {
        "type": "neoforge:add_spawns",
        "biomes": "minecraft:deep_dark",
        "spawners": spawners,
    })


def write_loot():
    """A self-drop table for every block with an item (upstream's tables use
    tool predicates and the 26.3 loot format differs; see NOTICE.md)."""
    for name in block_item_names():
        write_json(os.path.join(CONTENT, "data", NS, "loot_table", "blocks", name + ".json"), {
            "type": "minecraft:block",
            "pools": [{
                "rolls": 1,
                "bonus_rolls": 0,
                "entries": [{"type": "minecraft:item", "name": f"{NS}:{name}"}],
                "condition": {"type": "minecraft:survives_explosion"},
            }],
            "random_sequence": f"{NS}:blocks/{name}",
        })


TAG_IDS = set()


def collect_tag_ids(up):
    TAG_IDS.update(TAGS)
    for folder in ("block", "item"):
        base = os.path.join(up, "data", NS, "tags", folder)
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                if name.endswith(".json"):
                    rel = os.path.relpath(os.path.join(dirpath, name), base).replace("\\", "/")
                    TAG_IDS.add(f"{NS}:{rel[:-5]}")


def write_recipes(up):
    """Upstream's 1.21.1 recipes whose items the port registers, in 26.3's
    shape (ingredients are item ids or #tags; the result is {id, count})."""
    known = {f"{NS}:{n}" for n in block_item_names() + list(ITEMS) + tool_item_names() + armor_item_names()}
    vanilla = VANILLA_ITEMS
    src = os.path.join(up, "data", NS, "recipe")
    kept = 0
    for name in sorted(os.listdir(src)):
        if not name.endswith(".json"):
            continue
        recipe = read_json(os.path.join(src, name))

        def resolve(value):
            if isinstance(value, dict) and "item" in value:
                return value["item"]
            if isinstance(value, dict) and "tag" in value:
                return "#" + value["tag"]
            return None

        def exists(value):
            item = resolve(value)
            if item is None:
                return False
            if item.startswith("#"):
                return item[1:] in TAG_IDS
            return item in known or item in vanilla

        keys = {}
        ok = True
        for key, value in recipe.get("key", {}).items():
            if not exists(value):
                ok = False
                break
            keys[key] = resolve(value)
        if not ok:
            continue
        if "ingredients" in recipe:
            ingredients = []
            for value in recipe["ingredients"]:
                values = value if isinstance(value, list) else [value]
                if not all(exists(v) for v in values):
                    ok = False
                    break
                ingredients.append([resolve(v) for v in values] if isinstance(value, list) else resolve(value))
            if not ok:
                continue
        result = recipe.get("result", {})
        out = result.get("id")
        if out is None or (out not in known and out not in vanilla):
            continue
        effect = recipe.get("type", "")
        if effect not in ("minecraft:crafting_shaped", "minecraft:crafting_shapeless",
                          "minecraft:smelting", "minecraft:blasting",
                          "minecraft:stonecutting", "minecraft:smithing_transform"):
            continue
        decl = {"type": effect}
        if effect == "minecraft:crafting_shaped":
            decl["pattern"] = recipe["pattern"]
            decl["key"] = keys
        elif effect == "minecraft:crafting_shapeless":
            cats = recipe.get("category")
            if cats:
                decl["category"] = cats
            decl["ingredients"] = ingredients
        elif effect in ("minecraft:smelting", "minecraft:blasting"):
            decl["ingredient"] = resolve(recipe["ingredient"])
            decl["experience"] = recipe.get("experience", 0.0)
            decl["cookingtime"] = recipe.get("cookingtime", 200)
        elif effect == "minecraft:stonecutting":
            decl["ingredient"] = resolve(recipe["ingredient"])
        else:
            for key in ("template", "base", "addition"):
                value = recipe.get(key)
                if not exists(value):
                    ok = False
                    break
                decl[key] = resolve(value)
            if not ok:
                continue
        count = result.get("count", 1)
        decl["result"] = {"id": out}
        if count != 1:
            decl["result"]["count"] = count
        write_json(os.path.join(CONTENT, "data", NS, "recipe", name), decl)
        kept += 1
    return kept


# Vanilla items the port's recipes may name. Kept explicit so a recipe that
# names something the port cannot provide is dropped rather than broken.
VANILLA_ITEMS = set("""
minecraft:stick minecraft:coal minecraft:charcoal minecraft:iron_ingot
minecraft:gold_ingot minecraft:copper_ingot minecraft:netherite_ingot
minecraft:iron_nugget minecraft:gold_nugget minecraft:redstone
minecraft:lapis_lazuli minecraft:diamond minecraft:emerald minecraft:quartz
minecraft:amethyst_shard minecraft:echo_shard minecraft:bone
minecraft:bone_meal minecraft:string minecraft:leather minecraft:paper
minecraft:book minecraft:glass minecraft:glass_pane minecraft:sand
minecraft:gravel minecraft:clay_ball minecraft:brick minecraft:flint
minecraft:compass minecraft:clock minecraft:shears minecraft:bucket
minecraft:water_bucket minecraft:lava_bucket minecraft:bowl
minecraft:crafting_table minecraft:furnace minecraft:chest
minecraft:torch minecraft:ladder minecraft:scaffolding
minecraft:iron_block minecraft:gold_block minecraft:copper_block
minecraft:diamond_block minecraft:emerald_block minecraft:coal_block
minecraft:lapis_block minecraft:redstone_block minecraft:quartz_block
minecraft:obsidian minecraft:crying_obsidian minecraft:netherite_scrap
minecraft:netherrack minecraft:blackstone minecraft:polished_blackstone
minecraft:deepslate minecraft:cobbled_deepslate minecraft:tuff
minecraft:calcite minecraft:basalt minecraft:smooth_basalt
minecraft:sculk minecraft:sculk_vein minecraft:sculk_catalyst
minecraft:sculk_shrieker minecraft:sculk_sensor minecraft:echo_shard
minecraft:oak_planks minecraft:oak_log minecraft:oak_slab minecraft:oak_stairs
minecraft:oak_fence minecraft:oak_fence_gate minecraft:oak_door
minecraft:oak_trapdoor minecraft:oak_button minecraft:oak_pressure_plate
minecraft:oak_sign minecraft:oak_hanging_sign
minecraft:moss_block minecraft:vine minecraft:glow_lichen
minecraft:dirt minecraft:rooted_dirt minecraft:mud minecraft:soul_sand
minecraft:soul_soil minecraft:magma_block minecraft:glowstone
minecraft:shroomlight minecraft:froglight minecraft:verdant_froglight
minecraft:pearlescent_froglight minecraft:ochre_froglight
minecraft:sea_lantern minecraft:honey_block minecraft:honeycomb_block
minecraft:iron_sword minecraft:iron_pickaxe minecraft:iron_axe
minecraft:iron_shovel minecraft:iron_hoe minecraft:iron_helmet
minecraft:iron_chestplate minecraft:iron_leggings minecraft:iron_boots
minecraft:diamond_sword minecraft:diamond_pickaxe minecraft:diamond_axe
minecraft:diamond_shovel minecraft:diamond_hoe minecraft:diamond_helmet
minecraft:diamond_chestplate minecraft:diamond_leggings minecraft:diamond_boots
minecraft:netherite_sword minecraft:netherite_pickaxe minecraft:netherite_axe
minecraft:netherite_shovel minecraft:netherite_hoe minecraft:netherite_helmet
minecraft:netherite_chestplate minecraft:netherite_leggings minecraft:netherite_boots
minecraft:netherite_upgrade_smithing_template
minecraft:spyglass minecraft:recovery_compass minecraft:lodestone
minecraft:glow_berries minecraft:sweet_berries minecraft:bread
minecraft:wheat minecraft:sugar minecraft:egg minecraft:milk_bucket
minecraft:slime_ball minecraft:magma_cream minecraft:phantom_membrane
minecraft:gunpowder minecraft:blaze_powder minecraft:blaze_rod
minecraft:ender_pearl minecraft:ender_eye minecraft:nether_star
minecraft:experience_bottle minecraft:name_tag minecraft:saddle
minecraft:white_dye minecraft:black_dye minecraft:cyan_dye
minecraft:light_blue_dye minecraft:blue_dye minecraft:purple_dye
minecraft:magenta_dye minecraft:pink_dye minecraft:red_dye
minecraft:orange_dye minecraft:yellow_dye minecraft:lime_dye
minecraft:green_dye minecraft:brown_dye minecraft:gray_dye
minecraft:light_gray_dye
minecraft:white_wool minecraft:black_wool minecraft:cyan_wool
minecraft:string minecraft:feather minecraft:flint_and_steel
minecraft:fire_charge minecraft:end_crystal minecraft:netherite_ingot
minecraft:ancient_debris minecraft:respawn_anchor minecraft:crying_obsidian
minecraft:chain minecraft:iron_bars minecraft:lantern minecraft:soul_lantern
minecraft:campfire minecraft:soul_campfire minecraft:barrel minecraft:hopper
minecraft:dispenser minecraft:dropper minecraft:piston minecraft:sticky_piston
minecraft:observer minecraft:redstone_torch minecraft:repeater minecraft:comparator
minecraft:target minecraft:note_block minecraft:jukebox minecraft:bookshelf
minecraft:lectern minecraft:anvil minecraft:grindstone minecraft:smithing_table
minecraft:stonecutter minecraft:cartography_table minecraft:fletching_table
""".split())

# Tags the port writes, and the recipes may name as `#tag`.
TAGS = {
    "minecraft:mineable/pickaxe": STONE_TOOL_BLOCKS + [
        "sculk_stone_bricks", "sculk_stone_tiles", "soundproof_glass",
        "crystallized_amber", "gloomslate_light", "lite_block",
        "bordered_lite_block", "sculk_grime_bricks",
    ],
    "minecraft:mineable/axe": AXE_BLOCKS + ["blooming_stem", "stripped_blooming_stem"],
    "minecraft:mineable/shovel": SHOVEL_BLOCKS,
    "minecraft:needs_stone_tool": STONE_TOOL_BLOCKS,
    "minecraft:needs_iron_tool": IRON_TOOL_BLOCKS,
    "minecraft:swords": ["warden_sword", "resonarium_sword"],
    "minecraft:axes": ["warden_axe", "resonarium_axe"],
    "minecraft:pickaxes": ["warden_pickaxe", "resonarium_pickaxe"],
    "minecraft:shovels": ["warden_shovel", "resonarium_shovel"],
    "minecraft:hoes": ["warden_hoe", "resonarium_hoe"],
    NS + ":bloom_stem_connects": ["blooming_stem", "stripped_blooming_stem"],
}


def write_upstream_tags(up):
    """Upstream's item and block tags, with the entries this slice can name.
    A tag the port does not write is what a recipe's `#tag` may name."""
    known_items = {f"{NS}:{n}" for n in block_item_names() + list(ITEMS) + tool_item_names() + armor_item_names()}
    known_blocks = {f"{NS}:{n}" for n in list(BLOCKS) + list(SPECIAL)}
    for folder, known in (("item", known_items), ("block", known_blocks)):
        base = os.path.join(up, "data", NS, "tags", folder)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirs, files in os.walk(base):
            for name in files:
                if not name.endswith(".json"):
                    continue
                path = os.path.join(dirpath, name)
                rel = os.path.relpath(path, base).replace("\\", "/")
                data = read_json(path)
                values = [v for v in data.get("values", [])
                          if (v in known) or v.startswith("#minecraft:") or v.startswith("minecraft:")]
                target = os.path.join(CONTENT, "data", NS, "tags", folder, rel)
                if os.path.exists(target):
                    # Our own table for this tag: merge, keeping one entry each.
                    existing = read_json(target)
                    values = list(dict.fromkeys(existing["values"] + values))
                    data = {"values": values}
                elif not values:
                    continue
                else:
                    data = {"values": values}
                write_json(target, data)


def write_tags():
    for tag, members in TAGS.items():
        namespace, path = tag.split(":", 1)
        kind, name = path.split("/", 1) if "/" in path else ("block", path)
        # mineable/* and needs_*_tool are block tags; tools are item tags.
        folder = "item" if kind in ("swords", "axes", "pickaxes", "shovels", "hoes") else "block"
        ids = []
        for member in members:
            if tag.startswith(NS + ":"):
                ids.append(f"{NS}:{member}")
            elif member in BLOCKS or member in SPECIAL:
                ids.append(f"{NS}:{member}")
            else:
                ids.append(f"minecraft:{member}")
        write_json(os.path.join(CONTENT, "data", namespace, "tags", folder, path + ".json"), {
            "values": ids,
        })


def write_creative_tab():
    order = block_item_names() + list(ITEMS) + tool_item_names() + armor_item_names()
    write_json(os.path.join(CONTENT, "data", NS, "horizon", "creative_tab", "deeper_and_darker.json"), {
        "title": f"itemGroup.{NS}",
        "icon": f"{NS}:warden_carapace",
        "items": [f"{NS}:{name}" for name in dict.fromkeys(order)],
    })


def write_manifest():
    with open(os.path.join(CONTENT, "horizon-mod.toml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"""id = "{NS}"
name = "Deeper and Darker"
version = "0.1.0"
description = "Sculk stone, gloomslate, echo and bloom wood, warden gear and the sculk mobs of the deep dark. A Horizon port of Kyanite Mods' Deeper and Darker (GPL-3.0); the Otherside dimension is not ported."
authors = ["Kyanite Mods", "Horizon port by the Saison 2 server"]
api = "0.2"
side = "both"
capabilities = ["registries"]
""")


def main():
    if len(sys.argv) != 2:
        die("usage: python -I tools/port.py <upstream resources dir>")
    up = os.path.abspath(sys.argv[1])
    if not os.path.isdir(os.path.join(up, "assets", NS)):
        die(f"{up} is not the upstream resources tree")
    clean()
    copy_assets(up)
    write_manifest()
    write_blocks()
    write_items()
    write_equipment(up)
    write_entity_types()
    write_loot()
    collect_tag_ids(up)
    recipes = write_recipes(up)
    write_tags()
    write_upstream_tags(up)
    write_creative_tab()
    write_item_definitions()
    print(f"port.py: {len(BLOCKS) + len(SPECIAL)} blocks, "
          f"{len(ITEMS) + len(tool_item_names()) + len(armor_item_names())} items, "
          f"{len(MOBS)} entity types, {recipes} recipes")


if __name__ == "__main__":
    main()
