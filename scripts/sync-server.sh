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

PLAYERS_FILE="$REPO_DIR/src/data/server_players.json"
STATS_FILE="$REPO_DIR/src/data/player_stats.json"
PUNISHMENTS_FILE="$REPO_DIR/src/data/punishments.json"
HISTORY_FILE="$REPO_DIR/src/data/player_history.json"

cd "$REPO_DIR"

git pull --rebase origin main

python3 -c "
import os, json, glob

data_dir = '$DATA_DIR'
players_out = '$PLAYERS_FILE'

data_files = glob.glob(os.path.join(data_dir, '*.dat'))
uuids = []
for f in sorted(data_files):
    name = os.path.basename(f)
    if name.endswith('.dat') and not name.endswith('.dat_old'):
        uuids.append(name[:-4])

with open(players_out, 'w', encoding='utf-8') as out:
    json.dump(uuids, out, indent=2)
"

python3 "$SCRIPT_DIR/extract_stats.py"
python3 "$SCRIPT_DIR/extract_punishments.py"
python3 "$SCRIPT_DIR/censor_names.py"

CHANGED=0
if [ -n "$(git status --porcelain "$PLAYERS_FILE")" ]; then
    git add "$PLAYERS_FILE"
    CHANGED=1
fi
if [ -n "$(git status --porcelain "$STATS_FILE")" ]; then
    git add "$STATS_FILE"
    CHANGED=1
fi
if [ -n "$(git status --porcelain "$PUNISHMENTS_FILE")" ]; then
    git add "$PUNISHMENTS_FILE"
    CHANGED=1
fi
if [ -n "$(git status --porcelain "$HISTORY_FILE")" ]; then
    git add "$HISTORY_FILE"
    CHANGED=1
fi

if [ "$CHANGED" -eq 1 ]; then
    git config user.name "derex smp"
    git config user.email "derex-smp@users.noreply.github.com"
    git commit -m "Auto-sync player roster, statistics, and punishments from server"
    git push origin main
fi
