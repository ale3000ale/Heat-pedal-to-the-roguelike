import { defineConfig } from 'vitest/config';
import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';

const publicHost = process.env.HEAT_PUBLIC_URL
	? new URL(process.env.HEAT_PUBLIC_URL).hostname
	: undefined;

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter()
		})
	],
	server: {
		host: '127.0.0.1',
		port: 5173,
		strictPort: true,
		allowedHosts: publicHost ? [publicHost] : [],
		proxy: {
			'/api': { target: 'http://127.0.0.1:8000', changeOrigin: false },
			'/media': { target: 'http://127.0.0.1:8000', changeOrigin: false }
		}
	},
	test: {
		expect: { requireAssertions: true },
		projects: [
			{
				extends: './vite.config.ts',
				test: {
					name: 'server',
					environment: 'node',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
				}
			}
		]
	}
});
