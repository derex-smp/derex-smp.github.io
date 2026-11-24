import os
import sys
import json
import glob
import gzip
import struct
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor

def get_first_played(dat_path):
    try:
        with gzip.open(dat_path, "rb") as f:
            content = f.read()
        idx = content.find(b"firstPlayed")
        if idx != -1:
            val = struct.unpack(">q", content[idx + 11:idx + 19])[0]
            if val > 0:
                return datetime.fromtimestamp(val / 1000, timezone.utc).strftime("%b %d, %Y")
    except Exception:
        pass
    return None

def extract_player_stats(filepath):
    uuid = os.path.basename(filepath)[:-5]
    if len(uuid) != 36:
        return uuid, None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return uuid, None
    except Exception:
        return uuid, None

    raw_stats = data.get("stats", {})
    if not isinstance(raw_stats, dict):
        return uuid, None

    custom = raw_stats.get("minecraft:custom", {})
    mined = raw_stats.get("minecraft:mined", {})
    killed = raw_stats.get("minecraft:killed", {})
    killed_by = raw_stats.get("minecraft:killed_by", {})
    used = raw_stats.get("minecraft:used", {})
    crafted = raw_stats.get("minecraft:crafted", {})
    broken = raw_stats.get("minecraft:broken", {})

    extracted = {}

    playtime = custom.get("minecraft:play_time", 0) or custom.get("minecraft:play_one_minute", 0)
    if playtime:
        extracted["playtime"] = playtime // 20

    walked = custom.get("minecraft:walk_one_cm", 0) + custom.get("minecraft:sprint_one_cm", 0) + custom.get("minecraft:crouch_one_cm", 0)
    if walked:
        extracted["walked"] = walked // 100000

    flown = custom.get("minecraft:aviate_one_cm", 0)
    if flown:
        extracted["flown"] = flown // 100000

    sailed = custom.get("minecraft:boat_one_cm", 0)
    if sailed:
        extracted["sailed"] = sailed // 100000

    ridden = custom.get("minecraft:horse_one_cm", 0) + custom.get("minecraft:pig_one_cm", 0) + custom.get("minecraft:strider_one_cm", 0)
    if ridden:
        extracted["ridden"] = ridden // 100000

    minecart = custom.get("minecraft:minecart_one_cm", 0)
    if minecart:
        extracted["minecart"] = minecart // 100000

    swum = custom.get("minecraft:swim_one_cm", 0)
    if swum:
        extracted["swum"] = swum // 100000

    dived = custom.get("minecraft:walk_under_water_one_cm", 0)
    if dived:
        extracted["dived"] = dived // 100000

    climbed = custom.get("minecraft:climb_one_cm", 0)
    if climbed:
        extracted["climbed"] = climbed // 100000

    fallen = custom.get("minecraft:fall_one_cm", 0)
    if fallen:
        extracted["fallen"] = fallen // 100000

    jumps = custom.get("minecraft:jump", 0)
    if jumps:
        extracted["jumps"] = jumps

    damage_dealt = custom.get("minecraft:damage_dealt", 0)
    if damage_dealt:
        extracted["damage_dealt"] = damage_dealt

    damage_taken = custom.get("minecraft:damage_taken", 0)
    if damage_taken:
        extracted["damage_taken"] = damage_taken

    damage_blocked = custom.get("minecraft:damage_blocked_by_shield", 0)
    if damage_blocked:
        extracted["damage_blocked"] = damage_blocked

    kills = custom.get("minecraft:player_kills", 0)
    if kills:
        extracted["kills"] = kills

    deaths = custom.get("minecraft:deaths", 0)
    if deaths:
        extracted["deaths"] = deaths

    mob_kills = custom.get("minecraft:mob_kills", 0)
    if mob_kills:
        extracted["mob_kills"] = mob_kills

    dragons = killed.get("minecraft:ender_dragon", 0)
    if dragons:
        extracted["dragons"] = dragons

    wardens = killed_by.get("minecraft:warden", 0)
    if wardens:
        extracted["wardens"] = wardens

    ghasts = killed.get("minecraft:ghast", 0)
    if ghasts:
        extracted["ghasts"] = ghasts

    shulkers = killed.get("minecraft:shulker", 0)
    if shulkers:
        extracted["shulkers"] = shulkers

    spiders = killed.get("minecraft:spider", 0) + killed.get("minecraft:cave_spider", 0)
    if spiders:
        extracted["spiders"] = spiders

    creepers = killed.get("minecraft:creeper", 0)
    if creepers:
        extracted["creepers"] = creepers

    endermen = killed.get("minecraft:enderman", 0)
    if endermen:
        extracted["endermen"] = endermen

    slimes = killed.get("minecraft:slime", 0) + killed.get("minecraft:magma_cube", 0)
    if slimes:
        extracted["slimes"] = slimes

    cows = killed.get("minecraft:cow", 0) + killed.get("minecraft:mooshroom", 0)
    if cows:
        extracted["cows"] = cows

    sheep = killed.get("minecraft:sheep", 0)
    if sheep:
        extracted["sheep"] = sheep

    wolves = killed.get("minecraft:wolf", 0)
    if wolves:
        extracted["wolves"] = wolves

    diamonds = mined.get("minecraft:diamond_ore", 0) + mined.get("minecraft:deepslate_diamond_ore", 0)
    if diamonds:
        extracted["diamonds"] = diamonds

    debris = mined.get("minecraft:ancient_debris", 0)
    if debris:
        extracted["debris"] = debris

    coal = mined.get("minecraft:coal_ore", 0) + mined.get("minecraft:deepslate_coal_ore", 0)
    if coal:
        extracted["coal"] = coal

    lapis = mined.get("minecraft:lapis_ore", 0) + mined.get("minecraft:deepslate_lapis_ore", 0)
    if lapis:
        extracted["lapis"] = lapis

    redstone = mined.get("minecraft:redstone_ore", 0) + mined.get("minecraft:deepslate_redstone_ore", 0)
    if redstone:
        extracted["redstone"] = redstone

    quartz = mined.get("minecraft:nether_quartz_ore", 0)
    if quartz:
        extracted["quartz"] = quartz

    obsidian = mined.get("minecraft:obsidian", 0) + mined.get("minecraft:crying_obsidian", 0)
    if obsidian:
        extracted["obsidian"] = obsidian

    stone = (
        mined.get("minecraft:stone", 0)
        + mined.get("minecraft:cobblestone", 0)
        + mined.get("minecraft:deepslate", 0)
        + mined.get("minecraft:cobbled_deepslate", 0)
        + mined.get("minecraft:andesite", 0)
        + mined.get("minecraft:diorite", 0)
        + mined.get("minecraft:granite", 0)
        + mined.get("minecraft:tuff", 0)
    )
    if stone:
        extracted["stone"] = stone

    netherrack = mined.get("minecraft:netherrack", 0)
    if netherrack:
        extracted["netherrack"] = netherrack

    excavator = sum(
        v
        for k, v in mined.items()
        if any(
            s in k
            for s in [
                "dirt",
                "grass_block",
                "sand",
                "gravel",
                "clay",
                "soul_sand",
                "soul_soil",
                "mud",
                "podzol",
            ]
        )
    )
    if excavator:
        extracted["excavator"] = excavator

    corals = sum(v for k, v in mined.items() if "coral" in k)
    if corals:
        extracted["corals"] = corals

    ice = sum(v for k, v in mined.items() if "ice" in k)
    if ice:
        extracted["ice"] = ice

    bamboo = mined.get("minecraft:bamboo", 0)
    if bamboo:
        extracted["bamboo"] = bamboo

    sugarcane = mined.get("minecraft:sugar_cane", 0)
    if sugarcane:
        extracted["sugarcane"] = sugarcane

    trees = sum(v for k, v in used.items() if "sapling" in k or "propagule" in k)
    if trees:
        extracted["trees"] = trees

    mushrooms = (
        mined.get("minecraft:red_mushroom", 0)
        + mined.get("minecraft:brown_mushroom", 0)
        + mined.get("minecraft:crimson_fungus", 0)
        + mined.get("minecraft:warped_fungus", 0)
    )
    if mushrooms:
        extracted["mushrooms"] = mushrooms

    armor = sum(
        v
        for k, v in crafted.items()
        if any(
            k.endswith(p)
            for p in [
                "_helmet",
                "_chestplate",
                "_leggings",
                "_boots",
                "_cap",
                "_tunic",
                "_pants",
            ]
        )
    )
    if armor:
        extracted["armor"] = armor

    weapons = sum(
        v
        for k, v in crafted.items()
        if any(
            k.endswith(p) or k == f"minecraft:{p}"
            for p in ["_sword", "_axe", "bow", "crossbow", "trident", "mace", "shield"]
        )
    )
    if weapons:
        extracted["weapons"] = weapons

    bundles = sum(v for k, v in crafted.items() if "bundle" in k)
    if bundles:
        extracted["bundles"] = bundles

    tnt = crafted.get("minecraft:tnt", 0)
    if tnt:
        extracted["tnt"] = tnt

    baker = (
        crafted.get("minecraft:bread", 0)
        + crafted.get("minecraft:cake", 0)
        + crafted.get("minecraft:cookie", 0)
        + crafted.get("minecraft:pumpkin_pie", 0)
    )
    if baker:
        extracted["baker"] = baker

    scaffolding = used.get("minecraft:scaffolding", 0)
    if scaffolding:
        extracted["scaffolding"] = scaffolding

    torches = (
        used.get("minecraft:torch", 0)
        + used.get("minecraft:soul_torch", 0)
        + used.get("minecraft:redstone_torch", 0)
    )
    if torches:
        extracted["torches"] = torches

    redstone_placed = sum(
        v
        for k, v in used.items()
        if any(
            x in k
            for x in [
                "redstone",
                "repeater",
                "comparator",
                "observer",
                "piston",
                "dispenser",
                "dropper",
                "hopper",
                "lever",
                "daylight_detector",
                "tripwire_hook",
                "pressure_plate",
                "target",
                "sculk_sensor",
            ]
        )
    )
    if redstone_placed:
        extracted["redstone_placed"] = redstone_placed

    rails = sum(v for k, v in used.items() if "rail" in k)
    if rails:
        extracted["rails"] = rails

    signs = sum(v for k, v in used.items() if "sign" in k)
    if signs:
        extracted["signs"] = signs

    enchanted = custom.get("minecraft:enchant_item", 0)
    if enchanted:
        extracted["enchanted"] = enchanted

    grindstone = custom.get("minecraft:interact_with_grindstone", 0)
    if grindstone:
        extracted["grindstone"] = grindstone

    loom = custom.get("minecraft:interact_with_loom", 0)
    if loom:
        extracted["loom"] = loom

    shears = used.get("minecraft:shears", 0)
    if shears:
        extracted["shears"] = shears

    sponges = crafted.get("minecraft:sponge", 0)
    if sponges:
        extracted["sponges"] = sponges

    fish_eaten = (
        used.get("minecraft:cooked_cod", 0)
        + used.get("minecraft:cooked_salmon", 0)
        + used.get("minecraft:cod", 0)
        + used.get("minecraft:salmon", 0)
        + used.get("minecraft:tropical_fish", 0)
        + used.get("minecraft:pufferfish", 0)
    )
    if fish_eaten:
        extracted["fish_eaten"] = fish_eaten

    raw_meat = (
        used.get("minecraft:beef", 0)
        + used.get("minecraft:porkchop", 0)
        + used.get("minecraft:mutton", 0)
        + used.get("minecraft:chicken", 0)
        + used.get("minecraft:rabbit", 0)
        + used.get("minecraft:rotten_flesh", 0)
    )
    if raw_meat:
        extracted["raw_meat"] = raw_meat

    junk_food = (
        used.get("minecraft:cookie", 0)
        + used.get("minecraft:rotten_flesh", 0)
        + used.get("minecraft:spider_eye", 0)
        + used.get("minecraft:poisonous_potato", 0)
        + used.get("minecraft:dried_kelp", 0)
    )
    if junk_food:
        extracted["junk_food"] = junk_food

    soups = (
        used.get("minecraft:mushroom_stew", 0)
        + used.get("minecraft:beetroot_soup", 0)
        + used.get("minecraft:rabbit_stew", 0)
        + used.get("minecraft:suspicious_stew", 0)
    )
    if soups:
        extracted["soups"] = soups

    gapples = used.get("minecraft:golden_apple", 0) + used.get("minecraft:enchanted_golden_apple", 0)
    if gapples:
        extracted["gapples"] = gapples

    potions = (
        used.get("minecraft:potion", 0)
        + used.get("minecraft:splash_potion", 0)
        + used.get("minecraft:lingering_potion", 0)
    )
    if potions:
        extracted["potions"] = potions

    water_buckets = used.get("minecraft:water_bucket", 0)
    if water_buckets:
        extracted["water_buckets"] = water_buckets

    goat_horns = used.get("minecraft:goat_horn", 0)
    if goat_horns:
        extracted["goat_horns"] = goat_horns

    bells = custom.get("minecraft:bell_ring", 0)
    if bells:
        extracted["bells"] = bells

    records = custom.get("minecraft:play_record", 0)
    if records:
        extracted["records"] = records

    tools_broken = sum(broken.values())
    if tools_broken:
        extracted["tools_broken"] = tools_broken

    bred = custom.get("minecraft:animals_bred", 0)
    if bred:
        extracted["animals_bred"] = bred

    trades = custom.get("minecraft:traded_with_villager", 0)
    if trades:
        extracted["trades"] = trades

    pearls = used.get("minecraft:ender_pearl", 0)
    if pearls:
        extracted["pearls"] = pearls

    totems = used.get("minecraft:totem_of_undying", 0)
    if totems:
        extracted["totems"] = totems

    used_beds = sum(v for k, v in used.items() if k.endswith("_bed"))
    slept = custom.get("minecraft:sleep_in_bed", 0)
    beds_blown = max(0, used_beds - slept)
    if beds_blown:
        extracted["beds_blown"] = beds_blown

    dat_path = os.path.join(os.path.dirname(os.path.dirname(filepath)), "playerdata", f"{uuid}.dat")
    if os.path.isfile(dat_path):
        first_joined = get_first_played(dat_path)
        if first_joined:
            extracted["first_joined"] = first_joined

    return uuid, extracted

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)

    stats_dir = None
    if len(sys.argv) > 1:
        stats_dir = sys.argv[1]
    elif os.environ.get("PELICAN_STATS_DIR"):
        stats_dir = os.environ.get("PELICAN_STATS_DIR")
    else:
        server_path_file = os.path.join(repo_dir, ".server_path")
        if os.path.isfile(server_path_file):
            with open(server_path_file, "r", encoding="utf-8") as f:
                data_dir = f.read().strip()
                stats_dir = os.path.join(os.path.dirname(data_dir.rstrip("/\\")), "stats")

    if not stats_dir or not os.path.isdir(stats_dir):
        print(f"Stats directory '{stats_dir}' not found. Skipping stats extraction.", file=sys.stderr)
        return

    output_path = os.path.join(repo_dir, "src", "data", "player_stats.json")
    stat_files = glob.glob(os.path.join(stats_dir, "*.json"))

    master_stats = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        for uuid, stats in executor.map(extract_player_stats, stat_files):
            if stats:
                master_stats[uuid] = stats

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(master_stats, out, indent=2)

    print(f"Successfully extracted stats for {len(master_stats)} players.")

if __name__ == "__main__":
    main()
