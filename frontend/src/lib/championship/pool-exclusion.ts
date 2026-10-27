import type { CardEntry } from '$lib/types';
import { isBaseCard, isUploadedCard } from '../cards/card-origin';

// Gruppi di carte della pool di base escludibili in un colpo solo nella creazione
// di una pool personalizzata: le carte caricate a mano dall'admin e quelle di base.
export type CardGroup = 'caricate' | 'base';

// Azzera le copie scelte di tutte le carte del gruppo richiesto nel modulo «Nuova pool»,
// lasciando invariate le scelte dell'altro gruppo e quelle delle carte di nessuno dei due
// gruppi (per esempio le carte di partenza).
// Parametri: cards, le carte della pool di base; picks, le copie scelte per nome;
// group, il gruppo da escludere. Ritorna: una nuova mappa delle scelte, senza mutare
// `picks`. Non tocca il database: l'effetto vale solo per il modulo di creazione.
export function excludeCardGroup(
	cards: CardEntry[],
	picks: Record<string, number>,
	group: CardGroup
): Record<string, number> {
	const next = { ...picks };
	for (const card of cards) {
		const inGroup = group === 'caricate' ? isUploadedCard(card) : isBaseCard(card);
		if (inGroup) next[card.name] = 0;
	}
	return next;
}
