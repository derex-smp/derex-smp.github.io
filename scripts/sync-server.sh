#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -n "$PELICAN_PLAYERS_DIR" ]; then
    DATA_DIR="$PELICAN_PLAYERS_DIR"
elif [ -f "$REPO_DIR/.server_path" ]; then
    DATA_DIR="$(tr -d '\r\n' < "$REPO_DIR/.server_path")"
elif [ -n "$1" ]; then
    DATA_DIR="$1"
else
    echo "Error: Server data directory not configured. Create .server_path or pass path as argument." >&2
    exit 1
fi

if [ ! -d "$DATA_DIR" ]; then
    echo "Error: Directory '$DATA_DIR' does not exist." >&2
    exit 1
fi

OUTPUT_FILE="$REPO_DIR/src/data/server_players.json"

cd "$REPO_DIR"

git pull --rebase origin main

python3 -c "
import os, json, glob, sys

data_dir = '$DATA_DIR'
files = glob.glob(os.path.join(data_dir, '*.dat'))
uuids = []

for f in sorted(files):
    name = os.path.basename(f)
    if name.endswith('.dat') and not name.endswith('.dat_old'):
        uuids.append(name[:-4])

with open('$OUTPUT_FILE', 'w', encoding='utf-8') as out:
    json.dump(uuids, out, indent=2)
"

if [ -n "$(git status --porcelain "$OUTPUT_FILE")" ]; then
    git config user.name "Derex SMP"
    git config user.email "derex-smp@users.noreply.github.com"
    git add "$OUTPUT_FILE"
    git commit -m "Auto-sync player UUIDs from server"
    git push origin main
fi
