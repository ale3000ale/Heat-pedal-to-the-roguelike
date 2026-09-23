// frontend/src/lib/store/theme.ts
// Store globale per il tema chiaro/scuro, persistito in localStorage e applicato via classe "dark".

import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'heat_theme';

// loadInitialTheme()
// Nessun parametro.
// Legge il tema salvato in localStorage, o usa la preferenza del sistema operativo come default.
function loadInitialTheme(): Theme {
	if (!browser) return 'light';
	const saved = localStorage.getItem(STORAGE_KEY) as Theme | null;
	if (saved === 'light' || saved === 'dark') return saved;
	return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export const themeStore = writable<Theme>(loadInitialTheme());

// applyTheme(theme)
// theme: 'light' oppure 'dark'.
// Aggiunge/rimuove la classe "dark" su <html> (usata da Tailwind darkMode: 'class') e salva la scelta.
export function applyTheme(theme: Theme): void {
	if (!browser) return;
	document.documentElement.classList.toggle('dark', theme === 'dark');
	localStorage.setItem(STORAGE_KEY, theme);
}

// toggleTheme()
// Nessun parametro.
// Inverte il tema corrente (light<->dark), aggiorna lo store e applica la classe sul documento.
export function toggleTheme(): void {
	themeStore.update((current) => {
		const next: Theme = current === 'light' ? 'dark' : 'light';
		applyTheme(next);
		return next;
	});
}
