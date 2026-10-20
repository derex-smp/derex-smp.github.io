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
      serialize: (item) => {
        const now = new Date();
        if (item.url === "https://derex-smp.github.io/") {
          item.priority = 1.0;
          item.changefreq = "daily";
          item.lastmod = now;
        } else if (item.url.includes("/rules") || item.url.includes("/notbanlist")) {
          item.priority = 0.9;
          item.changefreq = "weekly";
          item.lastmod = now;
        } else if (item.url.includes("/members")) {
          item.priority = 0.8;
          item.changefreq = "hourly";
          item.lastmod = now;
        } else if (item.url.includes("/player/")) {
          item.priority = 0.7;
          item.changefreq = "hourly";
          item.lastmod = now;
        }
        return item;
      },
      chunks: {
        players: (item) => {
          if (item.url.includes("/player/")) {
            return item;
          }
          return false;
        },
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
