<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { beforeNavigate, goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import type { ChampionshipDetail, Pilot } from '$lib/types';
	import type { RaceDetail, RaceStatus } from '$lib/race-types';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import PilotGiftButton from '$lib/components/pilot-gift-button.svelte';
	import RaceReviewPanel from '$lib/components/race-review-panel.svelte';

	// Una riga della classifica: un pilota in ordine di arrivo con i suoi punti sponsor.
	interface Row {
		pilot_id: number;
		name: string;
		sponsor: number;
	}

	// Un pilota dichiarato a mano come non partecipante.
	interface Absent {
		pilot_id: number;
		name: string;
	}

	const MAX_PARTICIPANTS = 12;
	const inputClass =
		'h-8 w-20 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';

	// Etichetta e colore dello stato della gara.
	const STATUS_VIEW: Record<RaceStatus, { label: string; class: string }> = {
		in_progress: { label: 'in corso', class: 'text-red-600' },
		in_review: { label: 'in revisione', class: 'text-amber-600' },
		to_review: { label: 'da rivedere', class: 'text-amber-600' },
		closed: { label: 'terminata', class: 'text-green-600' }
	};

	let race = $state<RaceDetail | null>(null);
	let championship = $state<ChampionshipDetail | null>(null);
	let myPilots = $state<Pilot[]>([]);
	let order = $state<Row[]>([]);
	let absent = $state<Absent[]>([]);
	let error = $state<string | null>(null);
	let saveError = $state<string | null>(null);
	let saved = $state(false);
	let busy = $state(false);
	let leaveTarget = $state<URL | null>(null);
	let allowLeave = false;

	let myIds = $derived(new Set(myPilots.map((p) => p.id)));
	// Una gara con almeno un risultato ha la classifica registrata, altrimenti è in corso.
	let isRaceClosed = $derived(race !== null && race.participants > 0);
	// Il giudice può terminare una gara in corso; solo l'admin può correggerne una terminata.
	// Un campionato chiuso è in sola lettura per tutti.
	let canEdit = $derived(
		championship !== null &&
			!championship.is_closed &&
			auth.canManageRaces &&
			(!isRaceClosed || auth.canCorrectRaces)
	);
	// Il tasto S compare solo a giudice e admin, con la gara in corso e il campionato aperto.
	let canGift = $derived(
		championship !== null && !championship.is_closed && auth.canManageRaces && !isRaceClosed
	);
	// Il pannello di revisione compare a giudice e admin mentre la revisione è attiva, e solo
	// all'admin sull'ultima gara quando è da rivedere. Nelle gare precedenti non compare.
	let canReview = $derived(
		championship !== null &&
			!championship.is_closed &&
			auth.canManageRaces &&
			race !== null &&
			(race.status === 'in_review' ||
				(auth.canCorrectRaces && race.is_last && race.status === 'to_review'))
	);
	// Iscritti non ancora assegnati né alla classifica né ai non partecipanti.
	let available = $derived(
		race
			? race.results.filter(
					(r) =>
						!order.some((row) => row.pilot_id === r.pilot_id) &&
						!absent.some((a) => a.pilot_id === r.pilot_id)
				)
			: []
	);
	// Si può terminare solo con almeno un pilota in classifica e tutti gli altri dichiarati.
	let canFinish = $derived(order.length > 0 && available.length === 0);
	// Uscire dalla pagina con una classifica non salvata chiede conferma.
	let needsGuard = $derived(canEdit && !isRaceClosed && order.length > 0);

	// La data può mancare nelle gare create prima della data automatica.
	function raceDate(value: string | null): string {
		return value ? new Date(value).toLocaleDateString('it-IT') : 'Data da definire';
	}

	// Riempie il modulo con i dati già registrati: classifica in ordine di arrivo e,
	// se la gara ha i risultati, chi non ha partecipato.
	function loadOrder(detail: RaceDetail) {
		order = detail.results
			.filter((r) => r.position !== null)
			.map((r) => ({ pilot_id: r.pilot_id, name: r.pilot_name, sponsor: r.sponsor_points }));
		ababsent_placeholder();
		absent =
			detail.participants > 0
				? detail.results
						.filter((r) => r.position === null)
						.map((r) => ({ pilot_id: r.pilot_id, name: r.pilot_name }))
				: [];
	}

	function addToOrder(pilotId: number) {
		const found = race?.results.find((r) => r.pilot_id === pilotId);
		if (!found || order.length >= MAX_PARTICIPANTS) return;
		order.push({ pilot_id: found.pilot_id, name: found.pilot_name, sponsor: 0 });
	}

	function removeFromOrder(index: number) {
		order.splice(index, 1);
	}

	function addToAbsent(pilotId: number) {
		const found = race?.results.find((r) => r.pilot_id === pilotId);
		if (!found) return;
		absent.push({ pilot_id: found.pilot_id, name: found.pilot_name });
	}

	function removeFromAbsent(index: number) {
		absent.splice(index, 1);
	}

	// Sposta un pilota di una posizione: delta -1 sale, +1 scende.
	function move(index: number, delta: -1 | 1) {
		const target = index + delta;
		if (target < 0 || target >= order.length) return;
		const [row] = order.splice(index, 1);
		order.splice(target, 0, row);
	}

	// Il campo numerico può restare vuoto: lo trattiamo come 0 e non accettiamo negativi.
	function cleanSponsor(value: unknown): number {
		const n = Math.trunc(Number(value));
		return Number.isFinite(n) && n > 0 ? n : 0;
	}

	async function save(event: SubmitEvent) {
		event.preventDefault();
		if (!canFinish) return;
		saveError = null;
		saved = false;
		busy = true;
		try {
			const updated = await api<RaceDetail>(
				`/championships/${page.params.id}/races/${page.params.raceId}/results`,
				{
					method: 'PUT',
					body: {
						results: order.map((row) => ({
							pilot_id: row.pilot_id,
							sponsor_points: cleanSponsor(row.sponsor)
						})),
						absent: absent.map((a) => a.pilot_id)
					}
				}
			);
			race = updated;
			loadOrder(updated);
			saved = true;
		} catch (e) {
			saveError = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}

	// Con una classifica non terminata blocca l'uscita: nella navigazione interna mostra
	// il popup, in chiusura/ricarica della scheda usa l'avviso del browser.
	beforeNavigate(({ cancel, to, willUnload }) => {
		if (allowLeave || !needsGuard) return;
		cancel();
		if (!willUnload && to) leaveTarget = to.url;
	});

	async function confirmLeave() {
		const target = leaveTarget;
		leaveTarget = null;
		if (!target) return;
		allowLeave = true;
		// eslint-disable-next-line svelte/no-navigation-without-resolve
		await goto(target.pathname + target.search + target.hash);
	}

	onMount(async () => {
		try {
			[race, championship, myPilots] = await Promise.all([
				api<RaceDetail>(`/championships/${page.params.id}/races/${page.params.raceId}`),
				api<ChampionshipDetail>(`/championships/${page.params.id}`),
				api<Pilot[]>('/pilots')
			]);
			loadOrder(race);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		}
	});
</script>
