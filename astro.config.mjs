import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import { ensureAvatarsBaked } from "./src/scripts/bakeAvatars.ts";
import { updateAllPlayerNames } from "./src/scripts/updatePlayerNames.ts";

export default defineConfig({
  site: "https://derex-smp.github.io",
  vite: {
    plugins: [tailwindcss()],
  },
  integrations: [
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
