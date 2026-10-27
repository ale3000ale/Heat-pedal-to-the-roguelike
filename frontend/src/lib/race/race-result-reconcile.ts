import type { RaceResult } from './race-types';

export interface ResultRow {
	pilot_id: number;
	name: string;
	sponsor: RaceResult['sponsor_points'] | undefined;
}

export interface ResultForm {
	order: ResultRow[];
	absent: { pilot_id: number; name: string }[];
}

/** Verifica form coerente; lancia RangeError per ID ripetuti fra o dentro le liste. */
function assertAssignment(form: ResultForm): void {
	const ids = [...form.order, ...form.absent].map((row) => row.pilot_id);
	if (new Set(ids).size !== ids.length) {
		throw new RangeError('Un pilota non puo essere assegnato due volte');
	}
}

/** Confronta assegnazioni: ordine significativo, ordine degli assenti irrilevante. */
function sameAssignment(a: ResultForm, b: ResultForm): boolean {
	const ordered = a.order.map((row) => row.pilot_id);
	const other = b.order.map((row) => row.pilot_id);
	const absent = new Set(a.absent.map((row) => row.pilot_id));
	return (
		ordered.length === other.length &&
		ordered.every((id, index) => id === other[index]) &&
		a.absent.length === b.absent.length &&
		b.absent.every((row) => absent.has(row.pilot_id))
	);
}

/**
 * Rileva differenze da una base senza considerare i nomi come campi editabili.
 * @param base Ultimo modulo autorevole ricevuto dal server.
 * @param local Modulo attuale; undefined conserva un input sponsor svuotato.
 * @returns true per assegnazione o sponsor differenti; nessuna mutazione.
 * @throws RangeError per assegnazioni duplicate.
 */
export function hasResultChanges(base: ResultForm, local: ResultForm): boolean {
	assertAssignment(base);
	assertAssignment(local);
	if (!sameAssignment(base, local)) return true;
	const values = new Map(base.order.map((row) => [row.pilot_id, row.sponsor]));
	return local.order.some((row) => !Object.is(row.sponsor, values.get(row.pilot_id)));
}

/**
 * Merge a tre vie del modulo risultati, senza letture, scritture o effetti UI.
 * @param base Ultimo snapshot server; dopo PUT puo essere il modulo inviato.
 * @param local Modulo attuale, incluse eventuali modifiche durante la PUT.
 * @param remote Nuovo modulo autorevole, nello stesso contesto gara/utente.
 * @returns form indipendente, conflitto, assegnazione preservata e modifiche residue.
 * @throws RangeError per assegnazioni duplicate in qualsiasi input.
 * Ordine/assenti sono un unico gruppo. Nessuna validazione di permessi o salvataggio:
 * la pagina deve gestire stato gara, sola lettura, ID non piu validi e cambio contesto.
 */
export function reconcileResults(base: ResultForm, local: ResultForm, remote: ResultForm) {
	[base, local, remote].forEach(assertAssignment);
	const baseRows = new Map(base.order.map((row) => [row.pilot_id, row]));
	const remoteRows = new Map(remote.order.map((row) => [row.pilot_id, row]));
	const names = new Map([...remote.order, ...remote.absent].map((row) => [row.pilot_id, row.name]));
	const dirty = new Set(
		local.order
			.filter((row) => {
				const previous = baseRows.get(row.pilot_id);
				return !previous || !Object.is(previous.sponsor, row.sponsor);
			})
			.map((row) => row.pilot_id)
	);
	const lostDirty = [...dirty].some((id) => !remoteRows.has(id));
	const assignmentKept = !sameAssignment(base, local) || lostDirty;
	const source = assignmentKept ? local : remote;
	const localRows = new Map(local.order.map((row) => [row.pilot_id, row]));
	let conflict = assignmentKept && !sameAssignment(base, remote) && !sameAssignment(local, remote);
	const form: ResultForm = {
		order: source.order.map((row) => {
			const own = localRows.get(row.pilot_id);
			const fresh = remoteRows.get(row.pilot_id);
			const previous = baseRows.get(row.pilot_id);
			const keep = own !== undefined && dirty.has(row.pilot_id);
			if (keep && fresh && !Object.is(own.sponsor, fresh.sponsor)) {
				if (!previous || !Object.is(previous.sponsor, fresh.sponsor)) conflict = true;
			}
			return {
				pilot_id: row.pilot_id,
				name: names.get(row.pilot_id) ?? row.name,
				sponsor: keep ? own.sponsor : fresh ? fresh.sponsor : 0
			};
		}),
		absent: source.absent.map((row) => ({
			pilot_id: row.pilot_id,
			name: names.get(row.pilot_id) ?? row.name
		}))
	};
	return { form, conflict, assignmentKept, hasChanges: hasResultChanges(remote, form) };
}
