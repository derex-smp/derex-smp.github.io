import fs from 'node:fs';
import path from 'node:path';

interface PunishmentEntry {
  name: string;
  uuid: string;
  punishmentDate: number;
}

interface PlayerRecord {
  name: string;
  uuid: string;
}

const punishmentsPath = path.resolve('docs/deduplicated_punishments.json');
const outputDir = path.resolve('public/avatars');

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const rawData = fs.readFileSync(punishmentsPath, 'utf8');
const punishments: PunishmentEntry[] = JSON.parse(rawData);

const uniquePlayers: PlayerRecord[] = [];
const seen = new Set<string>();

for (const entry of punishments) {
  if (entry.uuid && !seen.has(entry.uuid)) {
    seen.add(entry.uuid);
    uniquePlayers.push({ uuid: entry.uuid, name: entry.name });
  }
}

async function fetchAvatar(player: PlayerRecord): Promise<void> {
  const filePath = path.join(outputDir, `${player.uuid}.png`);
  if (fs.existsSync(filePath)) {
    return;
  }

  const primaryUrl = `https://mc-heads.net/avatar/${player.uuid}/100`;
  const fallbackUrl = `https://minotar.net/avatar/${encodeURIComponent(player.name)}/100`;

  try {
    let res = await fetch(primaryUrl);
    if (!res.ok && player.name) {
      res = await fetch(fallbackUrl);
    }
    if (res.ok) {
      const buffer = Buffer.from(await res.arrayBuffer());
      fs.writeFileSync(filePath, buffer);
      console.log(`Saved avatar for ${player.name} (${player.uuid})`);
    } else {
      console.error(`Failed to fetch avatar for ${player.name} (${player.uuid}): status ${res.status}`);
    }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(`Error fetching avatar for ${player.name}:`, message);
  }
}

async function run(): Promise<void> {
  console.log(`Baking avatars for ${uniquePlayers.length} unique records...`);
  for (const player of uniquePlayers) {
    await fetchAvatar(player);
    await new Promise((resolve) => setTimeout(resolve, 60));
  }
  console.log('Avatar baking complete.');
}

run();
