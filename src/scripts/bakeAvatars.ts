import fs from 'node:fs';
import path from 'node:path';

interface PlayerRecord {
  name?: string;
  uuid: string;
}

const punishmentsPath = path.resolve('docs/deduplicated_punishments.json');
const playerdataDir = path.resolve('docs/playerdata');
const usercachePath = path.resolve('docs/usercache.json');
const outputDir = path.resolve('public/avatars');

async function fetchAvatar(player: PlayerRecord, current: number, total: number): Promise<void> {
  const filePath = path.join(outputDir, `${player.uuid}.png`);
  if (fs.existsSync(filePath)) {
    return;
  }

  const sources = [
    { name: 'mc-heads', url: `https://mc-heads.net/avatar/${player.uuid}/100` },
    ...(player.name ? [{ name: 'minotar', url: `https://minotar.net/avatar/${encodeURIComponent(player.name)}/100` }] : []),
    { name: 'crafatar', url: `https://crafatar.com/avatars/${player.uuid}?size=100&overlay` }
  ];

  for (const source of sources) {
    try {
      const res = await fetch(source.url);
      if (res.ok) {
        const buffer = Buffer.from(await res.arrayBuffer());
        if (buffer.length > 500) {
          fs.writeFileSync(filePath, buffer);
          console.log(`[${current}/${total}] Saved avatar for ${player.name || player.uuid} via ${source.name}`);
          return;
        }
      }
    } catch {}
  }

  console.error(`[${current}/${total}] Could not resolve skin for ${player.name || player.uuid}`);
}

export async function ensureAvatarsBaked(): Promise<void> {
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const nameMap = new Map<string, string>();
  if (fs.existsSync(usercachePath)) {
    try {
      const entries: { uuid: string; name: string }[] = JSON.parse(fs.readFileSync(usercachePath, 'utf8'));
      for (const entry of entries) {
        if (entry.uuid && entry.name) {
          nameMap.set(entry.uuid, entry.name);
          nameMap.set(entry.uuid.replace(/-/g, ''), entry.name);
        }
      }
    } catch {}
  }

  const uniquePlayers: PlayerRecord[] = [];
  const seen = new Set<string>();

  if (fs.existsSync(punishmentsPath)) {
    const punishments: { uuid: string; name?: string }[] = JSON.parse(fs.readFileSync(punishmentsPath, 'utf8'));
    for (const entry of punishments) {
      if (entry.uuid && !seen.has(entry.uuid)) {
        seen.add(entry.uuid);
        uniquePlayers.push({ uuid: entry.uuid, name: entry.name || nameMap.get(entry.uuid) });
      }
    }
  }

  if (fs.existsSync(playerdataDir)) {
    const files = fs.readdirSync(playerdataDir);
    for (const file of files) {
      if (file.endsWith('.dat') && !file.includes('_old')) {
        const uuid = file.replace('.dat', '');
        if (!seen.has(uuid)) {
          seen.add(uuid);
          uniquePlayers.push({ uuid, name: nameMap.get(uuid) });
        }
      }
    }
  }

  const missing = uniquePlayers.filter((p) => !fs.existsSync(path.join(outputDir, `${p.uuid}.png`)));
  if (missing.length === 0) {
    return;
  }

  console.log(`Baking ${missing.length} missing avatars (${uniquePlayers.length} total players)...`);

  const concurrency = 8;
  let index = 0;
  let completed = 0;
  const workers = Array.from({ length: Math.min(concurrency, missing.length) }, async () => {
    while (index < missing.length) {
      const item = missing[index++];
      await fetchAvatar(item, ++completed, missing.length);
    }
  });

  await Promise.all(workers);
  console.log('Avatar baking complete.');
}
