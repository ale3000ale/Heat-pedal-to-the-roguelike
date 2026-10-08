import { describe, expect, it, vi } from 'vitest';
import { ApiError } from './api';
import { buyPack, fetchInventory, fetchMyShops, fetchShop } from './shop-api';

type Fetcher = typeof fetch & ReturnType<typeof vi.fn>;

function fakeFetch(status: number, body: unknown): Fetcher {
	const fn = vi.fn(async () => new Response(JSON.stringify(body), { status }));
	return fn as unknown as Fetcher;
}

function lastCall(fn: ReturnType<typeof vi.fn>): [string, RequestInit] {
	return fn.mock.calls[0] as unknown as [string, RequestInit];
}

describe('shop-api', () => {
	it("legge i negozi dell'utente da /api/me/shops", async () => {
		const f = fakeFetch(200, { shops: [] });
		expect(await fetchMyShops(f)).toEqual({ shops: [] });
		expect(lastCall(f)[0]).toBe('/api/me/shops');
	});

	it('apre il negozio con o senza pilota', async () => {
		const withPilot = fakeFetch(200, {});
		await fetchShop(3, 7, withPilot);
		expect(lastCall(withPilot)[0]).toBe('/api/championships/3/shop?pilot_id=7');

		const without = fakeFetch(200, {});
		await fetchShop(3, undefined, without);
		expect(lastCall(without)[0]).toBe('/api/championships/3/shop');
	});

	it('acquista con POST e corpo pilot_id/pack_id', async () => {
		const f = fakeFetch(201, { purchase_id: 1 });
		await buyPack(3, 7, 9, f);
		const [url, init] = lastCall(f);
		expect(url).toBe('/api/championships/3/shop/purchases');
		expect(init.method).toBe('POST');
		expect(JSON.parse(init.body as string)).toEqual({ pilot_id: 7, pack_id: 9 });
	});

	it("legge l'inventario del pilota", async () => {
		const f = fakeFetch(200, {});
		await fetchInventory(3, 7, f);
		expect(lastCall(f)[0]).toBe('/api/championships/3/shop/inventory?pilot_id=7');
	});

	it('propaga il messaggio di errore del backend', async () => {
		const f = fakeFetch(409, { detail: 'Saldo insufficiente' });
		await expect(buyPack(3, 7, 9, f)).rejects.toMatchObject({
			status: 409,
			message: 'Saldo insufficiente'
		});
		await expect(buyPack(3, 7, 9, f)).rejects.toBeInstanceOf(ApiError);
	});
});
