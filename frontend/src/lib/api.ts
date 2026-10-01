// Errore lanciato quando il backend risponde con uno stato diverso da 2xx
// (o quando non è raggiungibile: in quel caso lo stato è 0).
// Le pagine lo intercettano per mostrare un messaggio all'utente.
export class ApiError extends Error {
	status: number;

	constructor(status: number, message: string) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
	}
}

type Options = {
	method?: string;
	body?: unknown;
	// Permette di passare un fetch diverso: usato nei test, e più avanti
	// dalle funzioni `load` di SvelteKit (che hanno un loro fetch).
	fetch?: typeof fetch;
};

// Legge il corpo della risposta come JSON. Se il corpo è vuoto o non è
// JSON valido restituisce null invece di lanciare un errore.
async function readJson(response: Response): Promise<unknown> {
	try {
		return await response.json();
	} catch {
		return null;
	}
}

// Ricava un messaggio leggibile dalla risposta di errore del backend.
// FastAPI manda {"detail": "testo"} per gli errori normali e una lista di
// oggetti per gli errori di validazione (422): in quel caso usiamo un testo generico.
function extractMessage(status: number, data: unknown): string {
	if (data && typeof data === 'object' && 'detail' in data) {
		const detail = (data as { detail: unknown }).detail;
		if (typeof detail === 'string') return detail;
	}
	if (status === 422) return 'Dati non validi';
	return `Errore ${status}`;
}

// Funzione unica con cui tutta l'app parla col backend.
// - Aggiunge da sola il prefisso /api (il proxy di Vite lo inoltra al server)
// - Invia i cookie di sessione (credentials: 'same-origin')
// - Converte il corpo in JSON e la risposta in oggetto
// - Lancia ApiError se qualcosa va storto
// Esempio: const utente = await api<User>('/auth/me');
export async function api<T = void>(
	path: string,
	{ method = 'GET', body, fetch: doFetch = fetch }: Options = {}
): Promise<T> {
	const headers: Record<string, string> = { Accept: 'application/json' };
	if (body !== undefined) headers['Content-Type'] = 'application/json';

	let response: Response;
	try {
		response = await doFetch(`/api${path}`, {
			method,
			headers,
			credentials: 'same-origin',
			body: body === undefined ? undefined : JSON.stringify(body)
		});
	} catch {
		// Errore di rete: server spento o connessione assente.
		throw new ApiError(0, 'Server non raggiungibile');
	}

	// 204 = successo senza corpo (per esempio il logout).
	if (response.status === 204) return undefined as T;

	const data = await readJson(response);

	if (!response.ok) {
		throw new ApiError(response.status, extractMessage(response.status, data));
	}
	return data as T;
}
