import { parseCardPoll } from './card-poll-validation';

// Logica del form admin per l'intervallo di controllo delle notifiche carta.
// Separata dal componente per poterla testare senza rete né interfaccia.

type CardPollSaved = { ok: true; seconds: number; message: string };
type CardPollFailed = { ok: false; message: string };
export type CardPollFormResult = CardPollSaved | CardPollFailed;

// Funzione che salva i secondi e ritorna l'impostazione confermata dal server.
export type SaveFn = (seconds: number) => Promise<{ seconds: number }>;

const SAVE_FAILED = 'Salvataggio non riuscito';

// Valida il testo digitato e, se corretto, lo salva.
// Parametri: `text` valore digitato dall'admin; `save` funzione di salvataggio
// (nel componente è `saveCardPoll`).
// Ritorna: esito con `ok: true` e il valore salvato, oppure `ok: false` e il messaggio.
// Errori: non lancia mai; un errore del server diventa un messaggio da mostrare.
export async function submitCardPoll(text: string, save: SaveFn): Promise<CardPollFormResult> {
	const parsed = parseCardPoll(text);
	if ('error' in parsed) return { ok: false, message: parsed.error };

	try {
		// Il valore mostrato è quello confermato dal server, non quello digitato.
		const saved = await save(parsed.seconds);
		const message = `Intervallo salvato: ${saved.seconds} secondi`;
		return { ok: true, seconds: saved.seconds, message };
	} catch (err) {
		const message = err instanceof Error ? err.message : SAVE_FAILED;
		return { ok: false, message };
	}
}
