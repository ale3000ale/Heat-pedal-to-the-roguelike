// Ruoli previsti dal backend: l'admin gestisce i campionati, il player i propri piloti.
export type Role = 'admin' | 'player';

// Utente come lo restituisce il backend (mai la password).
export interface User {
	id: number;
	username: string;
	role: Role;
}
