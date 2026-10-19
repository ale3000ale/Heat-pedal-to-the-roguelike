export interface ReviewInventoryCard {
	card_name: string;
	card_path: string;
	total: number;
	remaining: number;
	gifted: number;
	start: number;
	pool_now: number;
	pool_max: number | null;
}

export interface ReviewInventoryPilot {
	pilot_id: number;
	pilot_name: string;
	cards: ReviewInventoryCard[];
}

export interface ReviewInventory {
	race_id: number;
	pilots: ReviewInventoryPilot[];
}

export interface ReviewCounts {
	pilots: {
		pilot_id: number;
		cards: { card_name: string; remaining: number }[];
	}[];
}

export interface ReviewIncongruity {
	card_name: string;
	reason: string;
	pool_now: number;
	pool_after: number;
	pool_max: number | null;
}
