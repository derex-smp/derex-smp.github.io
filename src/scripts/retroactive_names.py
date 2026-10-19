# AI Generated script im going to use to backfill all the old punishment usernames now that we've set up a way to automate it in the future

import json
import os

def to_dashed(uuid_str):
    clean = uuid_str.replace("-", "").lower().strip()
    if len(clean) != 32:
        return uuid_str.lower().strip()
    return f"{clean[:8]}-{clean[8:12]}-{clean[12:16]}-{clean[16:20]}-{clean[20:]}"

base_dir = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(base_dir, "src")):
    base_dir = os.path.abspath(os.path.join(base_dir, ".."))

history_file = os.path.join(base_dir, "src", "data", "player_history.json")
punishments_file = os.path.join(base_dir, "src", "data", "punishments.json")
usercache_file = os.path.join(base_dir, "src", "data", "usercache.json")

history = {}
if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        history = json.load(f)

punishments = []
if os.path.exists(punishments_file):
    with open(punishments_file, "r", encoding="utf-8") as f:
        punishments = json.load(f)

usercache = []
if os.path.exists(usercache_file):
    with open(usercache_file, "r", encoding="utf-8") as f:
        usercache = json.load(f)

known_names = {}

for entry in punishments:
    name = entry.get("name")
    raw_uuid = entry.get("uuid")
    if name and raw_uuid:
        uuid = to_dashed(raw_uuid)
        known_names.setdefault(uuid, set()).add(name)

for entry in usercache:
    name = entry.get("name")
    raw_uuid = entry.get("uuid")
    if name and raw_uuid:
        uuid = to_dashed(raw_uuid)
        known_names.setdefault(uuid, set()).add(name)

updated_count = 0
added_count = 0

for uuid, names in known_names.items():
    if uuid in history:
        record = history[uuid]
        current_name = record.get("currentName", "")
        past_names = record.setdefault("pastNames", [])

        for old_name in names:
            if old_name.lower() != current_name.lower() and old_name not in past_names:
                past_names.append(old_name)
                updated_count += 1
                print(f"Updated {uuid}: current={current_name}, added past name={old_name}")
    else:
        name_list = list(names)
        history[uuid] = {
            "currentName": name_list[0],
            "pastNames": name_list[1:],
            "lastUpdated": ""
        }
        added_count += 1
        print(f"Created new entry for {uuid}: {name_list[0]}")

with open(history_file, "w", encoding="utf-8") as f:
    json.dump(history, f, indent=2)

print("\nDone!")
print(f"Past names added/updated: {updated_count}")
print(f"New history records created: {added_count}")
