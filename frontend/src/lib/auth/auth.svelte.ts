import { api, ApiError } from '../api';
import type { User } from '../types';

export class AuthStore {
	user = $state<User | null>(null);
	ready = $state(false);
	error = $state<string | null>(null);
	// Metadati del lifecycle UI, non identificativi o token della sessione server.
	sessionEpoch = $state(0);
	private pendingAuth = $state(0);

	get authenticating(): boolean {
		return this.pendingAuth > 0;
	}

	/** Chiave locale per isolare i dati draft; null durante transizioni o senza utente.
	 * Non viene inviata al server o persistita e non rappresenta un'autorizzazione.
	 */
	get sessionKey(): string | null {
		return this.ready && !this.authenticating && this.user
			? `${this.sessionEpoch}:${this.user.id}:${this.user.role}`
			: null;
	}

	get isAdmin(): boolean {
		return this.user?.role === 'admin';
	}
	get canManageRaces(): boolean {
		return this.user?.role === 'admin' || this.user?.role === 'judge';
	}
	get canCorrectRaces(): boolean {
		return this.user?.role === 'admin';
	}

	private beginAuth(): void {
		this.pendingAuth += 1;
		this.sessionEpoch += 1;
	}
	private endAuth(): void {
		this.pendingAuth -= 1;
	}

	/** Recupera l'utente corrente, conservando la gestione esistente di 401 ed errori. */
	async init(): Promise<void> {
		this.beginAuth();
		try {
			this.user = await api<User>('/auth/me');
			this.error = null;
		} catch (e) {
			this.user = null;
			if (!(e instanceof ApiError && e.status === 401)) {
				this.error = e instanceof Error ? e.message : 'Errore sconosciuto';
			}
		} finally {
			this.ready = true;
			this.endAuth();
		}
	}

	/** Login seguito da /auth/me; gli errori continuano a propagarsi al chiamante. */
	async login(username: string, password: string): Promise<void> {
		this.beginAuth();
		try {
			await api('/auth/login', { method: 'POST', body: { username, password } });
			this.user = await api<User>('/auth/me');
		} finally {
			this.endAuth();
		}
	}

	async register(username: string, password: string): Promise<void> {
		this.beginAuth();
		try {
			this.user = await api<User>('/auth/register', {
				method: 'POST',
				body: { username, password }
			});
		} finally {
			this.endAuth();
		}
	}

	/** Svuota l'utente anche se il logout fallisce; i dati draft sono invalidati subito. */
	async logout(): Promise<void> {
		this.beginAuth();
		try {
			await api('/auth/logout', { method: 'POST' });
		} finally {
			this.user = null;
			this.endAuth();
		}
	}
}

export const auth = new AuthStore();
