import { DOMAIN_EVENTS, type JsonValue, type StreamEvent } from './event-types';

function object(value: unknown): value is Record<string, unknown> {
	return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function positive(value: unknown): value is number {
	return typeof value === 'number' && Number.isSafeInteger(value) && value > 0;
}

function json(value: unknown): value is JsonValue {
	if (value === null || typeof value === 'string' || typeof value === 'boolean') return true;
	if (typeof value === 'number') return Number.isFinite(value);
	if (Array.isArray(value)) return value.every(json);
	return object(value) && Object.values(value).every(json);
}

/** Valida un cursore SQLite int64 senza convertirlo in un Number impreciso. */
function cursor(value: string): boolean {
	return /^(0|[1-9]\d{0,18})$/.test(value) && (value.length < 19 || value <= '9223372036854775807');
}

/**
 * Decodifica un evento del protocollo backend; non autorizza accessi alle API.
 * @param type Nome SSE ricevuto.
 * @param raw Corpo JSON non fidato.
 * @param id LastEventId mantenuto come stringa, anche oltre MAX_SAFE_INTEGER.
 * @returns Evento normalizzato o null per tipo, JSON o riferimenti invalidi.
 * Gli errori di parsing e le strutture eccessivamente annidate sono rifiutati.
 */
export function parseStreamEvent(type: string, raw: unknown, id: string): StreamEvent | null {
	try {
		if (typeof raw !== 'string') return null;
		const data: unknown = JSON.parse(raw);
		if (!object(data)) return null;
		if (type === 'auth.expired') {
			return Object.keys(data).length === 0 ? { type: 'auth.expired' } : null;
		}
		if (!cursor(id)) return null;
		if (type === 'resync') {
			const reason = data.reason;
			return reason === 'initial' || reason === 'cursor_unavailable'
				? { type: 'resync', id, reason }
				: null;
		}
		const domainType = DOMAIN_EVENTS.find((name) => name === type);
		if (!domainType || id === '0' || !positive(data.championship_id)) return null;
		if (data.pilot_id !== null && !positive(data.pilot_id)) return null;
		if (!object(data.payload) || !Object.values(data.payload).every(json)) return null;
		if ('race_id' in data.payload && !positive(data.payload.race_id)) return null;
		return {
			type: domainType,
			id,
			championshipId: data.championship_id,
			pilotId: data.pilot_id,
			payload: data.payload as Record<string, JsonValue>
		};
	} catch {
		return null;
	}
}
