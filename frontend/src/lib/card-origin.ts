import type { CardEntry, PoolKind } from '$lib/types';

// Prefisso del percorso relativo delle carte caricate a mano. Deve coincidere con quello
// usato dal backend (services/card_delete.py): solo queste carte si possono eliminare.
const UPLOADS_ROOT = 'cards/uploads/';

// Prefisso delle carte caricate di un tipo di pool.
// Parametri: kind, tipo di pool. Ritorna: il prefisso, per esempio 'cards/uploads/sponsor/'.
export function uploadsPrefix(kind: PoolKind): string {
	return `${UPLOADS_ROOT}${kind}/`;
}

// Dice se una carta è stata caricata a mano dall'admin (e quindi si può eliminare).
// Parametri: card, la carta (basta il percorso); kind, se indicato richiede anche che il
// tipo coincida. Ritorna: true per le carte caricate, false per quelle di base o di partenza.
export function isUploadedCard(card: Pick<CardEntry, 'path'>, kind?: PoolKind): boolean {
	const prefix = kind ? uploadsPrefix(kind) : UPLOADS_ROOT;
	return card.path.startsWith(prefix);
}
