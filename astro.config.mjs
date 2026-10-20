import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import { ensureAvatarsBaked } from "./src/scripts/bakeAvatars.ts";
import { updateAllPlayerNames } from "./src/scripts/updatePlayerNames.ts";
import sitemap from "@astrojs/sitemap";

import fs from "node:fs";
import path from "node:path";

const historyPath = path.resolve("src/data/player_history.json");
let canonicalNames = null;

function getCanonicalNames() {
  const names = new Set();
  if (fs.existsSync(historyPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(historyPath, "utf8"));
      for (const record of Object.values(data)) {
        if (record.currentName) {
          names.add(record.currentName.toLowerCase());
        }
      }
    } catch {}
  }
  return names;
}

export default defineConfig({
  site: "https://derex-smp.github.io",
  vite: {
    plugins: [tailwindcss()],
  },
  integrations: [
    sitemap({
      filter: (page) => {
        if (page.includes("/players/")) return false;
        const match = page.match(/\/player\/([^/]+)/);
        if (match) {
          if (!canonicalNames) {
            canonicalNames = getCanonicalNames();
          }
          const slug = decodeURIComponent(match[1]).toLowerCase();
          return canonicalNames.has(slug);
        }
        return true;
      },
    }),
    {
      name: "avatar-baker",
      hooks: {
        "astro:server:setup": async () => {
          await updateAllPlayerNames();
          await ensureAvatarsBaked();
        },
        "astro:build:start": async () => {
          await updateAllPlayerNames();
          await ensureAvatarsBaked();
        },
      },
    },
  ],
});
