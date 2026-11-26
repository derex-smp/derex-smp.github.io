import fs from "node:fs";
import path from "node:path";

interface HistoryRecord {
  currentName: string;
  pastNames: string[];
  lastUpdated: string;
}

const historyPath = path.resolve("src/data/player_history.json");
const playerdataDir = path.resolve("src/data/playerdata");
const serverPlayersPath = path.resolve("src/data/server_players.json");
const punishmentsPath = path.resolve("src/data/punishments.json");

function toDashed(clean: string): string {
  if (clean.length !== 32) return clean;
  return `${clean.slice(0, 8)}-${clean.slice(8, 12)}-${clean.slice(12, 16)}-${clean.slice(16, 20)}-${clean.slice(20)}`;
}

function toClean(dashed: string): string {
  return dashed.replace(/-/g, "");
}

async function fetchProfile(cleanUuid: string): Promise<string | null> {
  const sources = [
    `https://crafthead.net/profile/${cleanUuid}`,
    `https://sessionserver.mojang.com/session/minecraft/profile/${cleanUuid}`,
  ];

  for (const url of sources) {
    try {
      const res = await fetch(url);
      if (res.ok) {
        const json = await res.json();
        if (json && json.name) {
          return json.name;
        }
      }
    } catch {}
  }
  return null;
}

export async function updateAllPlayerNames(): Promise<void> {
  const history: Record<string, HistoryRecord> = fs.existsSync(historyPath)
    ? JSON.parse(fs.readFileSync(historyPath, "utf8"))
    : {};

  const allUuids = new Set<string>();

  if (fs.existsSync(serverPlayersPath)) {
    try {
      const uuids: string[] = JSON.parse(
        fs.readFileSync(serverPlayersPath, "utf8"),
      );
      for (const uuid of uuids) {
        allUuids.add(toClean(uuid));
      }
    } catch {}
  } else if (fs.existsSync(playerdataDir)) {
    for (const file of fs.readdirSync(playerdataDir)) {
      if (file.endsWith(".dat") && !file.includes("_old")) {
        allUuids.add(toClean(file.replace(".dat", "")));
      }
    }
  }

  if (fs.existsSync(punishmentsPath)) {
    try {
      const punishments: { uuid: string }[] = JSON.parse(
        fs.readFileSync(punishmentsPath, "utf8"),
      );
      for (const p of punishments) {
        if (p.uuid) {
          allUuids.add(toClean(p.uuid));
        }
      }
    } catch {}
  }

  const uuidList = Array.from(allUuids);
  const concurrency = 10;
  let index = 0;

  async function worker(): Promise<void> {
    while (index < uuidList.length) {
      const cleanUuid = uuidList[index++];
      const dashedUuid = toDashed(cleanUuid);
      const name = await fetchProfile(cleanUuid);

      if (name) {
        const current = history[dashedUuid] || history[cleanUuid];
        if (!current) {
          history[dashedUuid] = {
            currentName: name,
            pastNames: [],
            lastUpdated: new Date().toISOString(),
          };
        } else if (current.currentName !== name) {
          if (
            current.currentName !== "[Inappropriate Name]" &&
            current.currentName.toLowerCase() !== name.toLowerCase() &&
            !current.pastNames.some(
              (p) => p.toLowerCase() === current.currentName.toLowerCase(),
            )
          ) {
            current.pastNames.push(current.currentName);
          }
          current.currentName = name;
          current.lastUpdated = new Date().toISOString();
        }
      }
    }
  }

  await Promise.all(Array.from({ length: concurrency }, () => worker()));

  fs.writeFileSync(historyPath, JSON.stringify(history, null, 2), "utf8");
}
