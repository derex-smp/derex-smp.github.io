import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import { ensureAvatarsBaked } from './src/scripts/bakeAvatars.ts';

export default defineConfig({
	vite: {
		plugins: [tailwindcss()],
	},
	integrations: [
		{
			name: 'avatar-baker',
			hooks: {
				'astro:server:setup': async () => {
					await ensureAvatarsBaked();
				},
				'astro:build:start': async () => {
					await ensureAvatarsBaked();
				},
			},
		},
	],
});
