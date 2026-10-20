import { afterEach, describe, expect, it, vi } from 'vitest';
import { ApiError } from './api';
import {
	fetchChampionshipSnapshot,
	startChampionshipLive,
	type ChampionshipSnapshot
} from './championship-live';
import type { PilotGiftNotification } from './gift-notifications-api';
import type { ConnectionStatus, EventFilter, Listener, StreamEvent } from './events/event-types';

class FakeClient {
	status: ConnectionStatus = 'open';
	filter: EventFilter = {};
	events = new Set<Listener<StreamEvent>>();
	statuses = new Set<Listener<ConnectionStatus>>();

	subscribe(listener: Listener<StreamEvent>, filter: EventFilter = {}) {
		this.filter = filter;
		this.events.add(listener);
		return () => {
			this.events.delete(listener);
		};
	}

	subscribeStatus(listener: Listener<ConnectionStatus>) {
		this.statuses.add(listener);
		void listener(this.status);
		return () => {
			this.statuses.delete(listener);
		};
	}

	setStatus(status: ConnectionStatus) {
		this.status = status;
		for (const listener of this.statuses) void listener(status);
	}
}

function notification(id: number): PilotGiftNotification {
	return {
		pilotId: 1,
		gift: {
			id,
			race_id: 7,
			card_name: 'Sponsor',
			card_path: 'cards/sponsor.webp',
			created_at: '2026-10-20T21:00:00'
		}
	};
}

function snapshot(gifts: PilotGiftNotification[] = []): ChampionshipSnapshot {
	return {
		championship: {
			id: 3,
			name: 'Heat',
			date: '2026-10-20',
			is_closed: false,
			pilots_count: 1,
			pilots: [{ id: 1, name: 'Pilota', team_id: null, point: 0 }]
		},
		standings: [],
		races: [],
		myPilots: [
			{ id: 1, name: 'Pilota', team_id: null, gold: 0, sponsor: 0, point: 0 },
			{ id: 2, name: 'Non iscritto', team_id: null, gold: 0, sponsor: 0, point: 0 }
		],
		gifts
	};
}

const stops: (() => void)[] = [];
function setup() {
	const client = new FakeClient();
	let current = snapshot([notification(10)]);
	const load = vi.fn(async () => current);
	const onSnapshot = vi.fn<(value: ChampionshipSnapshot) => void>();
	const onGifts = vi.fn<(value: readonly PilotGiftNotification[]) => void>();
	const onError = vi.fn();
	const onUnauthorized = vi.fn();
	const f = vi.fn<typeof fetch>().mockResolvedValue(new Response(null, { status: 204 }));
	const live = startChampionshipLive({
		championshipId: 3,
		intervalMs: 1000,
		client,
		load,
		fetch: f,
		onSnapshot,
		onGifts,
		onError,
		onUnauthorized
	});
	stops.push(live.dispose);
	return {
		client,
		load,
		onSnapshot,
		onGifts,
		onError,
		onUnauthorized,
		f,
		live,
		setSnapshot: (value: ChampionshipSnapshot) => {
			current = value;
		}
	};
}

afterEach(() => {
	for (const stop of stops.splice(0)) stop();
	vi.useRealTimers();
});

describe('collegamento campionato', () => {
	it('legge notifiche solo dei piloti propri iscritti e le salta se chiuso', async () => {
		const value = snapshot();
		const f = vi.fn<typeof fetch>().mockImplementation(async (input) => {
			const url = String(input);
			const body = url.endsWith('/pilots')
				? value.myPilots
				: url.includes('/card-gifts?')
					? [notification(10).gift]
					: url.endsWith('/standings')
						? value.standings
						: url.endsWith('/races')
							? value.races
							: value.championship;
			return new Response(JSON.stringify(body), { status: 200 });
		});
		const read = await fetchChampionshipSnapshot(3, f);
		expect(read.gifts).toEqual([notification(10)]);
		expect(
			f.mock.calls.map(([url]) => String(url)).filter((url) => url.includes('card-gifts'))
		).toEqual(['/api/championships/3/card-gifts?pilot_id=1']);
		value.championship.is_closed = true;
		f.mockClear();
		expect((await fetchChampionshipSnapshot(3, f)).gifts).toEqual([]);
		expect(f.mock.calls.some(([url]) => String(url).includes('card-gifts'))).toBe(false);
	});

	it('collega popup e ack selettivo senza confermare i nuovi arrivi in coda', async () => {
		const { live, onGifts, f, setSnapshot } = setup();
		await live.refresh();
		setSnapshot(snapshot([notification(10), notification(20)]));
		await live.refresh();
		expect(onGifts.mock.calls.at(-1)?.[0]).toEqual([notification(10)]);
		await live.close([10]);
		expect(f).toHaveBeenCalledTimes(1);
		expect(f.mock.calls[0][0]).toBe('/api/championships/3/card-gifts/seen-selected');
		expect(JSON.parse(String(f.mock.calls[0][1]?.body))).toEqual({ pilot_id: 1, gift_ids: [10] });
		expect(onGifts.mock.calls.at(-1)?.[0]).toEqual([notification(20)]);
	});

	it('non chiude il popup dopo errore di lettura, ma lo riconcilia su snapshot vuoto riuscito', async () => {
		const { live, load, onGifts, onError, f, setSnapshot } = setup();
		await live.refresh();
		const count = onGifts.mock.calls.length;
		load.mockRejectedValueOnce(new ApiError(503, 'Non disponibile'));
		await live.refresh();
		expect(onError).toHaveBeenCalledOnce();
		expect(onGifts).toHaveBeenCalledTimes(count);
		setSnapshot(snapshot());
		await live.refresh();
		expect(onGifts.mock.calls.at(-1)?.[0]).toEqual([]);
		expect(f).not.toHaveBeenCalled();
	});

	it('non fa polling con stream open e usa il fallback solo quando necessario', async () => {
		vi.useFakeTimers();
		const { live, load, client } = setup();
		await live.refresh();
		const count = load.mock.calls.length;
		await vi.advanceTimersByTimeAsync(5000);
		expect(load).toHaveBeenCalledTimes(count);
		client.setStatus('retrying');
		await vi.advanceTimersByTimeAsync(1000);
		expect(load).toHaveBeenCalledTimes(count + 1);
		client.setStatus('open');
		await vi.advanceTimersByTimeAsync(5000);
		expect(load).toHaveBeenCalledTimes(count + 1);
		expect(client.filter).toEqual({ championshipId: 3 });
	});

	it('ferma letture, sottoscrizioni e conferme dopo 401', async () => {
		const { live, load, client, onUnauthorized, f } = setup();
		await live.refresh();
		load.mockRejectedValueOnce(new ApiError(401, 'Sessione scaduta'));
		await live.refresh();
		expect(onUnauthorized).toHaveBeenCalledOnce();
		expect(client.events.size).toBe(0);
		expect(client.statuses.size).toBe(0);
		const count = load.mock.calls.length;
		await live.refresh();
		await live.close([10]);
		expect(load).toHaveBeenCalledTimes(count);
		expect(f).not.toHaveBeenCalled();
	});

	it('scarta una risposta del contesto smontato', async () => {
		const { live, load, onSnapshot, onGifts, f } = setup();
		await live.refresh();
		let finish!: (value: ChampionshipSnapshot) => void;
		load.mockReturnValueOnce(
			new Promise<ChampionshipSnapshot>((resolve) => {
				finish = resolve;
			})
		);
		const pending = live.refresh();
		const count = onSnapshot.mock.calls.length;
		const giftsCount = onGifts.mock.calls.length;
		live.dispose();
		finish(snapshot([notification(20)]));
		await pending;
		await live.close([10]);
		expect(onSnapshot).toHaveBeenCalledTimes(count);
		expect(onGifts).toHaveBeenCalledTimes(giftsCount);
		expect(f).not.toHaveBeenCalled();
	});
});
