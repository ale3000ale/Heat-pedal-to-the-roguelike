import type { CardEntry } from './types';

export type DraftPhase = 'attendance' | 'order' | 'picking' | 'decks';

export interface DraftPilotRead {
	pilot_id: number;
	name: string;
	present: boolean;
}

export interface DraftCardSlot {
	slot_id: number;
	name: string;
	path: string;
	chosen_by: number | null;
}

export interface DraftRead {
	id: number;
	championship_id: number;
	version: number;
	phase: DraftPhase;
	first_race: boolean;
	can_manage: boolean;
	my_pilot_ids: number[];
	participants: DraftPilotRead[];
	order: number[];
	cards: DraftCardSlot[];
	picks: number[];
	preview_slot_id: number | null;
	ready: number[];
	current_pilot_id: number | null;
}

export interface DraftPilotDeckRead {
	pilot_id: number;
	preparation_version: number;
	ready: boolean;
	inventory_version: number;
	game_version: number;
	inventory: CardEntry[];
	game_deck: CardEntry[];
}

export interface DraftActionRead {
	preparation: DraftRead | null;
	race_id: number | null;
}

type Version = { version: number };

export interface DraftCommands {
	attendance: Version & { pilot_id: number; present: boolean };
	'attendance/confirm': Version;
	order: Version & { pilot_ids: number[] };
	start: Version;
	preview: Version & { slot_id: number | null };
	choice: Version & { slot_id: number };
	'deck/move': Version & { pilot_id: number; path: string; to_game: boolean };
	ready: Version & { pilot_id: number; ready: boolean };
	'already-disputed': Version;
	cancel: Version;
}

export type DraftCommandResult<K extends keyof DraftCommands> = K extends 'cancel'
	? void
	: K extends 'ready' | 'already-disputed'
		? DraftActionRead
		: DraftRead;
