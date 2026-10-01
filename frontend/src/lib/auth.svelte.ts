import { api, ApiError } from './api';
import type { User } from './types';

// Stato di autenticazione condiviso da tutta l'app.
// I campi $state sono "reattivi": quando cambiano, le pagine che li leggono
// si aggiornano da sole.
export class AuthStore {
	// Utente loggato, oppure null se nessuno ha una sessione valida.
	user = $state<User | null>(null);
	// false finché non sappiamo com'è la situazione (evita di mostrare per un
	// istante la pagina di login a chi è già dentro).
	ready = $state(false);
	// Ultimo errore di connessione, se il backend non risponde.
	error = $state<string | null>(null);

	// Vero se l'utente loggato è un amministratore.
	get isAdmin(): boolean {
		return this.user?.role === 'admin';
	}

	// Da chiamare una volta all'apertura dell'app: chiede al backend chi sono
	// (usando il cookie) e imposta lo stato di conseguenza.
	async init(): Promise<void> {
		try {
			this.user = await api<User>('/auth/me');
			this.error = null;
		} catch (e) {
			this.user = null;
			// 401 è normale (nessuna sessione); altri errori sono problemi veri.
			if (!(e instanceof ApiError && e.status === 401)) {
				this.error = e instanceof Error ? e.message : 'Errore sconosciuto';
			}
		} finally {
			this.ready = true;
		}
	}

	// Entra con username e password. Se i dati sono sbagliati lancia ApiError
	// (la pagina di login lo mostra). Poi rilegge l'utente da /auth/me.
	async login(username: string, password: string): Promise<void> {
		await api('/auth/login', { method: 'POST', body: { username, password } });
		this.user = await api<User>('/auth/me');
	}

	// Crea un nuovo account (sempre "player") e lo lascia loggato.
	async register(username: string, password: string): Promise<void> {
		this.user = await api<User>('/auth/register', {
			method: 'POST',
			body: { username, password }
		});
	}

	// Esce: cancella la sessione sul server e svuota lo stato locale.
	// Lo stato viene svuotato anche se la richiesta fallisce.
	async logout(): Promise<void> {
		try {
			await api('/auth/logout', { method: 'POST' });
		} finally {
			this.user = null;
		}
	}
}

// Unica istanza usata dall'app. I test creano istanze proprie con `new AuthStore()`.
export const auth = new AuthStore();
