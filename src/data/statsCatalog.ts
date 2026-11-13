export interface StatItem {
  id: string;
  name: string;
  category: "combat" | "mining" | "movement" | "building" | "quirks";
  d7: string;
  d30: string;
  total: string;
}

export interface StatDefinition {
  id: string;
  name: string;
  category: "combat" | "mining" | "movement" | "building" | "quirks";
  min: number;
  max: number;
  unit?: "km" | "time" | "damage" | "count";
}

function hashSeed(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function pseudoRand(seed: number, offset: number, min: number, max: number): number {
  const x = Math.sin(seed + offset) * 10000;
  const val = x - Math.floor(x);
  return Math.floor(val * (max - min + 1)) + min;
}

export const STAT_DEFINITIONS: StatDefinition[] = [
  { id: "playtime", name: "Playtime", category: "movement", min: 12, max: 2400, unit: "time" },
  { id: "walked", name: "Distance Walked", category: "movement", min: 20, max: 4500, unit: "km" },
  { id: "flown", name: "Distance Flown by Elytra", category: "movement", min: 5, max: 2200, unit: "km" },
  { id: "sailed", name: "Distance Sailed by Boat", category: "movement", min: 2, max: 800, unit: "km" },
  { id: "ridden", name: "Distance Ridden on Horse/Pig", category: "movement", min: 1, max: 1200, unit: "km" },
  { id: "minecart", name: "Distance Gone by Minecart", category: "movement", min: 1, max: 600, unit: "km" },
  { id: "swum", name: "Distance Swum", category: "movement", min: 2, max: 450, unit: "km" },
  { id: "dived", name: "Distance Dived Underwater", category: "movement", min: 1, max: 320, unit: "km" },
  { id: "climbed", name: "Distance Climbed", category: "movement", min: 1, max: 280, unit: "km" },
  { id: "fallen", name: "Distance Fallen", category: "movement", min: 2, max: 950, unit: "km" },
  { id: "jumps", name: "Total Jumps", category: "movement", min: 500, max: 65000, unit: "count" },

  { id: "damage_dealt", name: "Damage Dealt", category: "combat", min: 500, max: 180000, unit: "damage" },
  { id: "damage_taken", name: "Damage Taken", category: "combat", min: 200, max: 85000, unit: "damage" },
  { id: "damage_blocked", name: "Damage Blocked by Shield", category: "combat", min: 0, max: 35000, unit: "damage" },
  { id: "kills", name: "Player Kills", category: "combat", min: 0, max: 142, unit: "count" },
  { id: "deaths", name: "Deaths", category: "combat", min: 2, max: 280, unit: "count" },
  { id: "mob_kills", name: "Monsters Slain", category: "combat", min: 50, max: 12500, unit: "count" },
  { id: "dragons", name: "Ender Dragons Slain", category: "combat", min: 0, max: 24, unit: "count" },
  { id: "wardens", name: "Times Killed by Wardens", category: "combat", min: 0, max: 48, unit: "count" },
  { id: "ghasts", name: "Ghasts Killed", category: "combat", min: 0, max: 820, unit: "count" },
  { id: "shulkers", name: "Shulkers Killed", category: "combat", min: 0, max: 650, unit: "count" },
  { id: "spiders", name: "Spiders Killed", category: "combat", min: 5, max: 2400, unit: "count" },
  { id: "creepers", name: "Creepers Killed", category: "combat", min: 5, max: 3100, unit: "count" },
  { id: "endermen", name: "Endermen Killed", category: "combat", min: 2, max: 4200, unit: "count" },
  { id: "slimes", name: "Slimes Killed", category: "combat", min: 0, max: 1850, unit: "count" },
  { id: "cows", name: "Cows Slaughtered", category: "combat", min: 0, max: 1600, unit: "count" },
  { id: "sheep", name: "Sheep Slaughtered", category: "combat", min: 0, max: 1400, unit: "count" },
  { id: "wolves", name: "Wolves Slain", category: "combat", min: 0, max: 95, unit: "count" },

  { id: "diamonds", name: "Diamonds Mined", category: "mining", min: 0, max: 850, unit: "count" },
  { id: "debris", name: "Ancient Debris Mined", category: "mining", min: 0, max: 320, unit: "count" },
  { id: "coal", name: "Coal Ore Mined", category: "mining", min: 20, max: 8500, unit: "count" },
  { id: "lapis", name: "Lapis Lazuli Mined", category: "mining", min: 0, max: 1950, unit: "count" },
  { id: "redstone", name: "Redstone Ore Mined", category: "mining", min: 0, max: 4200, unit: "count" },
  { id: "quartz", name: "Nether Quartz Mined", category: "mining", min: 0, max: 6400, unit: "count" },
  { id: "obsidian", name: "Obsidian Mined", category: "mining", min: 0, max: 1250, unit: "count" },
  { id: "stone", name: "Stone Mined", category: "mining", min: 100, max: 75000, unit: "count" },
  { id: "netherrack", name: "Netherrack Mined", category: "mining", min: 50, max: 45000, unit: "count" },
  { id: "excavator", name: "Ground & Soil Dug", category: "mining", min: 50, max: 32000, unit: "count" },
  { id: "corals", name: "Corals Mined", category: "mining", min: 0, max: 1400, unit: "count" },
  { id: "ice", name: "Ice Broken", category: "mining", min: 0, max: 4800, unit: "count" },
  { id: "bamboo", name: "Bamboo Harvested", category: "mining", min: 0, max: 18500, unit: "count" },
  { id: "sugarcane", name: "Sugar Cane Harvested", category: "mining", min: 0, max: 14200, unit: "count" },
  { id: "trees", name: "Trees Planted", category: "mining", min: 0, max: 2400, unit: "count" },
  { id: "mushrooms", name: "Mushrooms Gathered", category: "mining", min: 0, max: 1650, unit: "count" },

  { id: "armor", name: "Armor Pieces Crafted", category: "building", min: 0, max: 450, unit: "count" },
  { id: "weapons", name: "Weapons Crafted", category: "building", min: 0, max: 380, unit: "count" },
  { id: "bundles", name: "Bundles Crafted", category: "building", min: 0, max: 85, unit: "count" },
  { id: "tnt", name: "TNT Crafted", category: "building", min: 0, max: 950, unit: "count" },
  { id: "baker", name: "Breads & Cakes Baked", category: "building", min: 0, max: 2400, unit: "count" },
  { id: "scaffolding", name: "Scaffolding Placed", category: "building", min: 0, max: 8500, unit: "count" },
  { id: "torches", name: "Torches Placed", category: "building", min: 10, max: 14500, unit: "count" },
  { id: "redstone_placed", name: "Redstone Devices Placed", category: "building", min: 0, max: 4800, unit: "count" },
  { id: "rails", name: "Rails Placed", category: "building", min: 0, max: 3200, unit: "count" },
  { id: "signs", name: "Signs Placed", category: "building", min: 0, max: 650, unit: "count" },
  { id: "enchanted", name: "Items Enchanted", category: "building", min: 0, max: 550, unit: "count" },
  { id: "grindstone", name: "Grindstone Interactions", category: "building", min: 0, max: 420, unit: "count" },
  { id: "loom", name: "Loom Interactions", category: "building", min: 0, max: 180, unit: "count" },
  { id: "shears", name: "Shears Durability Used", category: "building", min: 0, max: 2800, unit: "count" },
  { id: "sponges", name: "Wet Sponges Dried", category: "building", min: 0, max: 450, unit: "count" },

  { id: "fish_eaten", name: "Fish Eaten", category: "quirks", min: 0, max: 620, unit: "count" },
  { id: "raw_meat", name: "Raw Meat Consumed", category: "quirks", min: 0, max: 380, unit: "count" },
  { id: "junk_food", name: "Junkfood Items Eaten", category: "quirks", min: 0, max: 540, unit: "count" },
  { id: "soups", name: "Soups & Stews Eaten", category: "quirks", min: 0, max: 280, unit: "count" },
  { id: "gapples", name: "Golden Apples Eaten", category: "quirks", min: 0, max: 85, unit: "count" },
  { id: "potions", name: "Potions Used", category: "quirks", min: 0, max: 420, unit: "count" },
  { id: "water_buckets", name: "Water Buckets Emptied", category: "quirks", min: 0, max: 3200, unit: "count" },
  { id: "goat_horns", name: "Goat Horns Sounded", category: "quirks", min: 0, max: 750, unit: "count" },
  { id: "bells", name: "Bells Rung", category: "quirks", min: 0, max: 4200, unit: "count" },
  { id: "records", name: "Music Discs Played", category: "quirks", min: 0, max: 190, unit: "count" },
  { id: "tools_broken", name: "Tools Broken", category: "quirks", min: 0, max: 280, unit: "count" },
  { id: "animals_bred", name: "Animals Bred", category: "quirks", min: 0, max: 1250, unit: "count" },
  { id: "trades", name: "Villager Trades", category: "quirks", min: 0, max: 1800, unit: "count" },
  { id: "pearls", name: "Ender Pearls Thrown", category: "quirks", min: 0, max: 650, unit: "count" },
  { id: "totems", name: "Totems of Undying Popped", category: "quirks", min: 0, max: 35, unit: "count" },
  { id: "beds_blown", name: "Beds Blown Up", category: "quirks", min: 0, max: 58, unit: "count" },
];

export function getPlayerStats(uuidOrName: string): StatItem[] {
  const seed = hashSeed(uuidOrName);

  return STAT_DEFINITIONS.map((def, idx) => {
    const totalVal = pseudoRand(seed, idx * 3 + 1, def.min, def.max);
    const d30Val = Math.floor(totalVal * (pseudoRand(seed, idx * 3 + 2, 12, 35) / 100));
    const d7Val = Math.floor(d30Val * (pseudoRand(seed, idx * 3 + 3, 10, 35) / 100));

    let d7Str = String(d7Val);
    let d30Str = String(d30Val);
    let totalStr = totalVal.toLocaleString();

    if (def.unit === "time") {
      const daysPart = Math.floor(totalVal / 24);
      const hoursPart = totalVal % 24;
      totalStr = daysPart > 0 ? `${daysPart}d ${hoursPart}h` : `${hoursPart}h`;
      d30Str = `${Math.max(1, Math.floor(totalVal * 0.15))}h`;
      d7Str = `${Math.max(0, Math.floor(totalVal * 0.04))}h`;
    } else if (def.unit === "km") {
      totalStr = `${totalVal.toLocaleString()}km`;
      d30Str = `${d30Val.toLocaleString()}km`;
      d7Str = `${d7Val.toLocaleString()}km`;
    } else if (def.unit === "damage") {
      totalStr = totalVal.toLocaleString();
      d30Str = d30Val.toLocaleString();
      d7Str = d7Val.toLocaleString();
    } else {
      totalStr = totalVal.toLocaleString();
      d30Str = d30Val.toLocaleString();
      d7Str = d7Val.toLocaleString();
    }

    return {
      id: def.id,
      name: def.name,
      category: def.category,
      d7: d7Str,
      d30: d30Str,
      total: totalStr,
    };
  });
}
