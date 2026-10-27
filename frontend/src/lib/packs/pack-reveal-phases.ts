// Fasi e tempi dell'animazione di apertura di un pacchetto.
// Logica pura, senza DOM, per poterla provare con Vitest.

// Sequenza: busta chiusa, strappo, scorrimento verso il basso, carte in fila.
export type RevealPhase = 'sealed' | 'tearing' | 'sliding' | 'cards';

// Durata in millisecondi delle fasi che avanzano da sole.
export const PHASE_DURATIONS_MS = { tearing: 700, sliding: 600 } as const;

// Ritardo massimo di ingresso di una carta, per non allungare troppo i pacchetti grandi.
const MAX_CARD_DELAY_MS = 1200;
const CARD_STEP_MS = 120;

// Fase successiva a quella data; dopo `cards` non si va oltre.
// @param phase fase corrente.
// @returns la fase seguente.
export function nextPhase(phase: RevealPhase): RevealPhase {
	if (phase === 'sealed') return 'tearing';
	if (phase === 'tearing') return 'sliding';
	return 'cards';
}

// Fase di partenza: con il movimento ridotto si salta direttamente alle carte.
// @param reducedMotion vero se il sistema chiede meno animazioni.
// @returns la fase iniziale.
export function initialPhase(reducedMotion: boolean): RevealPhase {
	return reducedMotion ? 'cards' : 'sealed';
}

// Ritardo di ingresso della carta in posizione `index` (da 0), con tetto massimo.
// @param index posizione della carta nella fila.
// @returns millisecondi di attesa.
export function cardDelayMs(index: number): number {
	return Math.min(Math.max(index, 0) * CARD_STEP_MS, MAX_CARD_DELAY_MS);
}
