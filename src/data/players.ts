import {existsSync, readFileSync, readdirSync} from 'node:fs';
import {resolve} from 'node:path';

import punishments from './punishments.json';

interface HistoryRecord {
	currentName: string;
	pastNames?: string[];
}

interface Member {
	name: string;
	uuid: string;
	pastNames?: string[];
}

const historyPath = resolve('src/data/player_history.json');
const usercachePath = resolve('src/data/usercache.json');
const playerdataDir = resolve('src/data/playerdata');

const historyMap = new Map<string, HistoryRecord>();
if (existsSync(historyPath)) {
	try {
		const raw: Record<string, HistoryRecord> = JSON.parse(
			readFileSync(historyPath, 'utf8'),
		);
		for (const [id, record] of Object.entries(raw)) {
			historyMap.set(id, record);
			historyMap.set(id.replace(/-/g, ''), record);
		}
	} catch {}
}

const nameMap = new Map<string, string>();
if (existsSync(usercachePath)) {
	try {
		const entries: { uuid: string; name: string }[] = JSON.parse(
			readFileSync(usercachePath, 'utf8'),
		);
		for (const entry of entries) {
			if (entry.uuid && entry.name) {
				nameMap.set(entry.uuid, entry.name);
				nameMap.set(entry.uuid.replace(/-/g, ''), entry.name);
			}
		}
	} catch {}
}

const members: Member[] = [];
const seen = new Set<string>();

if (existsSync(playerdataDir)) {
	const files = readdirSync(playerdataDir);
	for (const file of files) {
		if (file.endsWith('.dat') && !file.includes('_old')) {
			const uuid = file.replace('.dat', '');
			const cleanUuid = uuid.replace(/-/g, '');
			if (!seen.has(uuid) && !seen.has(cleanUuid)) {
				seen.add(uuid);
				seen.add(cleanUuid);
				const hist = historyMap.get(uuid) || historyMap.get(cleanUuid);
				const name = hist?.currentName || nameMap.get(uuid) || nameMap.get(cleanUuid) || uuid.slice(0, 8);
				const pastNames = hist?.pastNames?.length ? hist.pastNames : undefined;
				members.push({ name, uuid, pastNames });
			}
		}
	}
}

const allMembers: Member[] = [...members];

for (const punished of punishments) {
    const uuid = punished.uuid;

    if (seen.has(uuid)) {
        continue;
    }

    seen.add(uuid);
    const hist = historyMap.get(uuid);
    const name = hist?.currentName || punished.name;
    const pastNames = hist?.pastNames?.length ? hist.pastNames : undefined;
    allMembers.push({ name, uuid, pastNames })
}

members.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }));
allMembers.sort((a, b) => a.name.localeCompare(b.name, undefined, { sensitivity: 'base' }));

export const getMembers = () => members;
export const getAllMembers = () => allMembers;
