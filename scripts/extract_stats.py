import os
import sys
import json
import glob
from concurrent.futures import ThreadPoolExecutor

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
    used = raw_stats.get("minecraft:used", {})

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

    ghasts = killed.get("minecraft:ghast", 0)
    if ghasts:
        extracted["ghasts"] = ghasts

    shulkers = killed.get("minecraft:shulker", 0)
    if shulkers:
        extracted["shulkers"] = shulkers

    diamonds = mined.get("minecraft:diamond_ore", 0) + mined.get("minecraft:deepslate_diamond_ore", 0)
    if diamonds:
        extracted["diamonds"] = diamonds

    debris = mined.get("minecraft:ancient_debris", 0)
    if debris:
        extracted["debris"] = debris

    trades = custom.get("minecraft:traded_with_villager", 0)
    if trades:
        extracted["trades"] = trades

    bred = custom.get("minecraft:animals_bred", 0)
    if bred:
        extracted["animals_bred"] = bred

    gapples = used.get("minecraft:golden_apple", 0) + used.get("minecraft:enchanted_golden_apple", 0)
    if gapples:
        extracted["gapples"] = gapples

    pearls = used.get("minecraft:ender_pearl", 0)
    if pearls:
        extracted["pearls"] = pearls

    totems = used.get("minecraft:totem_of_undying", 0)
    if totems:
        extracted["totems"] = totems

    bells = custom.get("minecraft:bell_ring", 0)
    if bells:
        extracted["bells"] = bells

    enchanted = custom.get("minecraft:enchant_item", 0)
    if enchanted:
        extracted["enchanted"] = enchanted

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
