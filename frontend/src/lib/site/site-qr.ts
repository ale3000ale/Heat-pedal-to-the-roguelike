import { api } from '$lib/api';

/** Indirizzo del sito e QR PNG (data URL) restituiti dal backend. */
export type SiteQr = {
	url: string;
	image: string;
};

/** Chiede al backend l'indirizzo pubblico e il QR per aprirlo da un altro dispositivo. */
export async function fetchSiteQr(fetchFn: typeof fetch = fetch): Promise<SiteQr> {
	return api<SiteQr>('/site/qr', { fetch: fetchFn });
}

/** Vero se l'indirizzo e raggiungibile solo dal PC, non da un telefono in rete. */
export function isLocalOnlyUrl(value: string): boolean {
	try {
		const { hostname } = new URL(value);
		return hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '[::1]';
	} catch {
		return false;
	}
}
