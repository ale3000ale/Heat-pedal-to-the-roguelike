// frontend/src/lib/api.ts
// Client HTTP centralizzato per parlare con il backend FastAPI, con gestione automatica del token JWT.

import { get } from 'svelte/store';
import { authStore, clearAuth } from '$lib/store/auth';

const BASE_URL = '/api'; // in dev viene proxato da vite.config.ts verso http://127.0.0.1:8000

interface RequestOptions {
	method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
	body?: unknown;
	auth?: boolean; // se true, aggiunge l'header Authorization con il JWT corrente
}

// apiRequest(path, options)
// path: endpoint relativo (es. "/pilots"); options: metodo HTTP, body JSON, flag auth.
// Effettua la fetch verso il backend, gestisce l'header Authorization e gli errori HTTP.
// Passaggio critico: se il backend risponde 401, la sessione locale viene invalidata (logout automatico).
export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
	const { method = 'GET', body, auth = false } = options;
	const headers: Record<string, string> = { 'Content-Type': 'application/json' };

	if (auth) {
		const state = get(authStore);
		if (state.token) headers['Authorization'] = `Bearer ${state.token}`;
	}

	const res = await fetch(`${BASE_URL}${path}`, {
		method,
		headers,
		body: body !== undefined ? JSON.stringify(body) : undefined
	});

	if (res.status === 401) {
		clearAuth();
	}

	if (!res.ok) {
		const errBody = await res.json().catch(() => ({ detail: res.statusText }));
		throw new Error(errBody.detail || `Errore richiesta: ${res.status}`);
	}

	if (res.status === 204) return undefined as T;
	return (await res.json()) as T;
}
