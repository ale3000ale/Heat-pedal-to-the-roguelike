import { parseCardPoll } from './card-poll-validation';

// Logica del form admin per l'intervallo di controllo delle notifiche carta.
// Separata dal componente per poterla testare senza rete né interfaccia.

export type CardPollFormResult =
	| { ok: true; seconds: number; message: string }
	| { ok: false; message: string };

// Valida il testo digitato e, se corretto, lo salva.
// Parametri: `text` valore digitato dall'admin; `save` funzione che salva i secondi
// e ritorna l'impostazione aggiornata (nel componente è `saveCardPoll`).
// Ritorna: `{ ok: true, seconds, message }` se salvato, altrimenti `{ ok: false, message }`.
// Errori: non lancia mai; un errore del server diventa un messaggio da mostrare.
export async function submitCardPoll(
	text: string,
	save: (seconds: number) => Promise<{ seconds: number }>
): Promise<CardPollFormResult> {
	const parsed = parseCardPoll(text);
	if ('error' in parsed) return { ok: false, message: parsed.error };

	try {
		// Il valore mostrato è quello confermato dal server, non quello digitato.
		const saved = await save(parsed.seconds);
		return {
			ok: true,
			seconds: saved.seconds,
			message: `Intervallo salvato: ${saved.seconds} secondi`
		};
	} catch (err) {
		const message = err instanceof Error ? err.message : 'Salvataggio non riuscito';
		return { ok: false, message };
	}
}
