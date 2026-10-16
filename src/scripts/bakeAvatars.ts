import fs from 'node:fs';
import path from 'node:path';

interface PunishmentEntry {
  name: string;
  uuid: string;
  punishmentDate: number;
}

interface PlayerRecord {
  name?: string;
  uuid: string;
}

const punishmentsPath = path.resolve('docs/deduplicated_punishments.json');
const playerdataDir = path.resolve('docs/playerdata');
const outputDir = path.resolve('public/avatars');

async function fetchAvatar(player: PlayerRecord, index: number, total: number): Promise<void> {
  const filePath = path.join(outputDir, `${player.uuid}.png`);
  if (fs.existsSync(filePath)) {
    return;
  }

  const sources = [
    { name: 'mc-heads', url: `https://mc-heads.net/avatar/${player.uuid}/100` },
    ...(player.name ? [{ name: 'minotar', url: `https://minotar.net/avatar/${encodeURIComponent(player.name)}/100` }] : []),
    { name: 'crafatar', url: `https://crafatar.com/avatars/${player.uuid}?size=100&overlay` },
  ];

  for (const source of sources) {
    try {
      const res = await fetch(source.url);
      if (res.ok) {
        const buffer = Buffer.from(await res.arrayBuffer());
        if (buffer.length > 500) {
          fs.writeFileSync(filePath, buffer);
          console.log(`[${index}/${total}] Saved avatar for ${player.name || player.uuid} via ${source.name}`);
          return;
        }
      }
    } catch {}
  }

  console.error(`[${index}/${total}] Could not resolve skin for ${player.name || player.uuid}`);
}

export async function ensureAvatarsBaked(): Promise<void> {
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const uniquePlayers: PlayerRecord[] = [];
  const seen = new Set<string>();

  if (fs.existsSync(punishmentsPath)) {
    const rawData = fs.readFileSync(punishmentsPath, 'utf8');
    const punishments: PunishmentEntry[] = JSON.parse(rawData);
    for (const entry of punishments) {
      if (entry.uuid && !seen.has(entry.uuid)) {
        seen.add(entry.uuid);
        uniquePlayers.push({ uuid: entry.uuid, name: entry.name });
      }
    }
  }

  if (fs.existsSync(playerdataDir)) {
    const files = fs.readdirSync(playerdataDir);
    for (const file of files) {
      if (file.endsWith('.dat') && !file.includes('_old')) {
        const rawUuid = file.replace('.dat', '');
        const cleanUuid = rawUuid.replace(/-/g, '');
        if (!seen.has(rawUuid)) {
          seen.add(rawUuid);
          uniquePlayers.push({ uuid: rawUuid });
        }
        if (!seen.has(cleanUuid)) {
          seen.add(cleanUuid);
          uniquePlayers.push({ uuid: cleanUuid });
        }
      }
    }
  }

  const missingPlayers = uniquePlayers.filter((p) => !fs.existsSync(path.join(outputDir, `${p.uuid}.png`)));

  if (missingPlayers.length === 0) {
    return;
  }

  console.log(`Baking ${missingPlayers.length} missing avatars into public/avatars/ (${uniquePlayers.length} total records)...`);
  for (let i = 0; i < missingPlayers.length; i++) {
    await fetchAvatar(missingPlayers[i], i + 1, missingPlayers.length);
    await new Promise((resolve) => setTimeout(resolve, 60));
  }
  console.log('Avatar baking complete.');
}
