import type { CardGroup, CardPlay } from './card-play-types';

// Raggruppa le giocate attive per carta, in ordine di prima comparsa.
// Le giocate annullate o consumate non contano: restano nel registro ma non si mostrano.
// Parametri: `plays` elenco delle giocate del pilota nella gara.
// Ritorna: un gruppo per carta con il numero di copie giocate ("x N").
export function groupActivePlays(plays: CardPlay[]): CardGroup[] {
	const groups = new Map<string, CardGroup>();
	for (const play of plays) {
		if (play.status !== 'giocata') continue;
		const key = play.card_name.toLowerCase();
		const existing = groups.get(key);
		if (existing) existing.count += 1;
		else groups.set(key, { name: play.card_name, path: play.card_path, count: 1 });
	}
	return [...groups.values()];
}

// Etichetta "x N" mostrata sulle copie uguali; vuota se la copia è una sola.
export function countLabel(count: number): string {
	return count > 1 ? `x ${count}` : '';
}
