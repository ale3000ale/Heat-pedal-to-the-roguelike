// frontend/src/lib/store/auth.ts
// Store globale per lo stato di autenticazione: token JWT, utente corrente, ruolo.

import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface AuthUser {
	username: string;
	role: 'user' | 'admin';
}

export interface AuthState {
	token: string | null;
	user: AuthUser | null;
}

const STORAGE_KEY = 'heat_auth';

// loadInitialState()
// Nessun parametro.
// Recupera token e utente salvati in localStorage all'avvio dell'app (solo lato browser),
// per mantenere la sessione attiva dopo un refresh della pagina.
function loadInitialState(): AuthState {
	if (!browser) return { token: null, user: null };
	const raw = localStorage.getItem(STORAGE_KEY);
	if (!raw) return { token: null, user: null };
	try {
		return JSON.parse(raw);
	} catch {
		return { token: null, user: null };
	}
}

export const authStore = writable<AuthState>(loadInitialState());

// setAuth(token, user)
// token: JWT ricevuto dal backend dopo login/registrazione; user: dati base dell'utente.
// Aggiorna lo store e persiste la sessione in localStorage, cosi' resta valida tra i refresh.
export function setAuth(token: string, user: AuthUser): void {
	const state: AuthState = { token, user };
	authStore.set(state);
	if (browser) localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

// clearAuth()
// Nessun parametro.
// Esegue il logout: azzera lo store e rimuove la sessione salvata, tornando alla vista "senza login".
export function clearAuth(): void {
	authStore.set({ token: null, user: null });
	if (browser) localStorage.removeItem(STORAGE_KEY);
}
