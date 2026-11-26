# just a band aid for now but it works pretty well, advancedban is never actually used outside of this logging method hahaha
import os
import sys
import json
import re
import csv
import glob

def find_storage_script(repo_dir):
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]

    env_path = os.environ.get("ADVANCEDBAN_SCRIPT")
    if env_path and os.path.isfile(env_path):
        return env_path

    server_path_file = os.path.join(repo_dir, ".server_path")
    if os.path.isfile(server_path_file):
        try:
            with open(server_path_file, "r", encoding="utf-8") as f:
                data_dir = f.read().strip()

            curr = data_dir.rstrip("/\\")
            for _ in range(5):
                candidate = os.path.join(curr, "plugins", "AdvancedBan", "data", "storage.script")
                if os.path.isfile(candidate):
                    return candidate
                candidate_root = os.path.join(curr, "storage.script")
                if os.path.isfile(candidate_root):
                    return candidate_root
                parent = os.path.dirname(curr)
                if parent == curr:
                    break
                curr = parent
        except Exception:
            pass

    candidates = []
    for pattern in [
        "/var/lib/pelican/volumes/*/plugins/AdvancedBan/data/storage.script",
        "/var/lib/pelican/volumes/*/storage.script",
        "D:/Server Migration/storage.script",
        "D:/Server Migration/plugins/AdvancedBan/data/storage.script",
    ]:
        matches = glob.glob(pattern)
        for m in matches:
            if os.path.isfile(m):
                candidates.append(m)

    if candidates:
        candidates.sort(key=os.path.getmtime, reverse=True)
        return candidates[0]

    return None

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)
    storage_path = find_storage_script(repo_dir)

    if not storage_path or not os.path.isfile(storage_path):
        print("AdvancedBan storage.script not found. Skipping punishment sync.", file=sys.stderr)
        return

    output_path = os.path.join(repo_dir, "src", "data", "punishments.json")

    punishments_by_uuid = {}

    with open(storage_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line_str = line.strip()
            if not line_str.startswith("INSERT INTO PUNISHMENTS VALUES") and not line_str.startswith("INSERT INTO punishments VALUES"):
                continue

            m = re.search(r"INSERT\s+INTO\s+PUNISHMENTS\s+VALUES\s*\((.*)\)\s*;?$", line_str, re.I)
            if not m:
                continue

            try:
                vals = list(csv.reader([m.group(1)], quotechar="'", skipinitialspace=True))[0]
                if len(vals) < 7:
                    continue

                name = vals[1].strip()
                raw_uuid = vals[2].strip().replace("-", "").lower()
                if len(raw_uuid) == 32:
                    uuid_str = f"{raw_uuid[:8]}-{raw_uuid[8:12]}-{raw_uuid[12:16]}-{raw_uuid[16:20]}-{raw_uuid[20:]}"
                else:
                    uuid_str = vals[2].strip()

                start_time = int(vals[6].strip())

                if raw_uuid not in punishments_by_uuid or start_time > punishments_by_uuid[raw_uuid]["punishmentDate"]:
                    punishments_by_uuid[raw_uuid] = {
                        "name": name,
                        "uuid": uuid_str,
                        "punishmentDate": start_time
                    }
            except Exception:
                continue

    records = list(punishments_by_uuid.values())
    records.sort(key=lambda x: x["punishmentDate"])

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(records, out, indent=2)

    print(f"Successfully extracted {len(records)} active punishments from {storage_path}.")

if __name__ == "__main__":
