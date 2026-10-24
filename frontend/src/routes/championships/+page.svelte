<script lang="ts">
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';
	import { api } from '$lib/api';
	import { auth } from '$lib/auth.svelte';
	import { groupChampionships, initiallyOpenGroup, type GroupKey } from '$lib/championship-groups';
	import type { Championship, Pilot } from '$lib/types';
	import { Button } from '$lib/components/ui/button';
	import ChampionshipSettings from '$lib/components/championship-settings.svelte';
	import NewChampionshipDialog from '$lib/components/new-championship-dialog.svelte';
	import RacingIcon from '$lib/components/racing-icon.svelte';

	// Messaggio mostrato quando una sezione non contiene campionati.
	const emptyMessages: Record<GroupKey, string> = {
		enrolled: 'Nessun campionato a cui partecipa la tua scuderia.',
		active: 'Nessun campionato attualmente attivo sui circuiti.',
		closed: 'Nessun campionato concluso in archivio.'
	};

	let championships = $state<Championship[]>([]);
	let pilots = $state<Pilot[]>([]);
	let loaded = $state(false);
	let error = $state<string | null>(null);
	let selectedId = $state<number | null>(null);
	let settingsOpen = $state(false);
	let newOpen = $state(false);
	let openGroups = $state<Record<GroupKey, boolean>>({
		enrolled: false,
		active: false,
		closed: false
	});

	let groups = $derived(groupChampionships(championships, pilots));
	let selected = $derived(championships.find((c) => c.id === selectedId) ?? null);

	// Carica campionati e piloti dell'utente loggato: servono entrambi per la sezione Iscritto.
	async function loadChampionships() {
		[championships, pilots] = await Promise.all([
			api<Championship[]>('/championships'),
			api<Pilot[]>('/pilots')
		]);
	}

	onMount(async () => {
		try {
			await loadChampionships();
			// Una sola sezione aperta all'arrivo; dopo, l'utente apre e chiude come preferisce.
			openGroups[initiallyOpenGroup(groups)] = true;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			loaded = true;
		}
	});

	function formatDate(value: string): string {
		return new Date(value).toLocaleDateString('it-IT', {
			day: '2-digit',
			month: 'short',
			year: 'numeric'
		});
	}

	function openSettings(championship: Championship) {
		selectedId = championship.id;
		settingsOpen = true;
	}

	function replaceChampionship(updated: Championship) {
		championships = championships.map((c) => (c.id === updated.id ? updated : c));
	}
</script>

<svelte:head><title>Campionati Grand Prix — Heat</title></svelte:head>

{#snippet list(items: Championship[], empty: string)}
	{#if items.length === 0}
		<p class="py-6 text-center text-xs text-muted-foreground italic">{empty}</p>
	{:else}
		<div class="grid gap-4 sm:grid-cols-2">
			{#each items as c (c.id)}
				<div class="group relative">
					<a href={resolve('/championships/[id]', { id: String(c.id) })} class="block">
						<div
							class="heat-card-hover curb-left overflow-hidden rounded-2xl border border-white/10 bg-[#141824] p-5 shadow-lg transition-all"
						>
							<div class="flex items-start justify-between gap-4">
								<div>
									<div class="mb-1.5 flex items-center gap-2">
										<span
											class="font-racing text-xs font-bold tracking-wider text-amber-400 uppercase"
										>
											Gran Premio #{c.id}
										</span>
									</div>
									<h3
										class="group-hover:text-heat font-racing text-2xl font-bold tracking-wide text-white uppercase transition-colors"
									>
										{c.name}
									</h3>
									<div class="mt-3 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
										<span class="inline-flex items-center gap-1 font-medium">
											<RacingIcon name="stopwatch" size="xs" />
											{formatDate(c.date)}
										</span>
										<span
											class="inline-flex items-center gap-1 rounded-full border border-white/10 bg-white/5 px-2 py-0.5 text-xs font-semibold text-foreground"
										>
											<RacingIcon name="helmet" size="xs" />
											{c.pilots_count}
											{c.pilots_count === 1 ? 'pilota iscritto' : 'piloti iscritti'}
										</span>
									</div>
								</div>
								<div
									class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-white"
								>
									<RacingIcon name="flags" size="sm" />
								</div>
							</div>
						</div>
					</a>
					{#if auth.isAdmin}
						<Button
							class="absolute top-3.5 right-3.5 h-8 w-8 rounded-lg border-white/10 bg-[#0e121a]/90 p-0 text-muted-foreground shadow-md backdrop-blur hover:border-amber-400 hover:text-amber-400"
							size="sm"
							variant="outline"
							aria-label={`Impostazioni di ${c.name}`}
							onclick={() => openSettings(c)}
						>
							<RacingIcon name="wrenches" size="xs" />
						</Button>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
{/snippet}

{#snippet section(
	key: GroupKey,
	title: string,
	items: Championship[],
	iconName: 'helmet' | 'flags' | 'trophy'
)}
	<details
		class="group/det overflow-hidden rounded-2xl border border-white/10 bg-[#10141e] shadow-xl"
		bind:open={openGroups[key]}
	>
		<summary
			class="flex cursor-pointer items-center justify-between bg-[#151926] px-5 py-4 font-racing text-xl font-bold tracking-wider text-white uppercase transition-colors select-none hover:bg-white/5"
		>
			<div class="flex items-center gap-3">
				<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/20 text-primary">
					<RacingIcon name={iconName} size="sm" />
				</div>
				<span>{title}</span>
				<span
					class="rounded-full bg-white/10 px-2 py-0.5 font-sans text-xs font-bold text-muted-foreground"
				>
					{items.length}
				</span>
			</div>
			<span class="text-xs text-muted-foreground transition-transform group-open/det:rotate-180"
				>▼</span
			>
		</summary>
		<div class="p-5">
			{@render list(items, emptyMessages[key])}
		</div>
	</details>
{/snippet}

<main class="mx-auto max-w-6xl space-y-6 px-4 py-8 sm:px-6">
	<!-- Page Header Banner -->
	<div class="relative mb-2 overflow-hidden rounded-2xl border border-white/10 shadow-xl">
		<!-- Board game photo background -->
		<div class="absolute inset-0 z-0">
			<img
				src="/images/heat-corner.jpg"
				alt="Heat board game corner"
				class="h-full w-full object-cover object-center opacity-20"
			/>
			<div
				class="absolute inset-0 bg-gradient-to-r from-[#10141e] via-[#10141e]/90 to-[#10141e]/60"
			></div>
		</div>
		<div
			class="relative z-10 flex flex-col justify-between gap-4 px-6 py-5 sm:flex-row sm:items-center"
		>
			<div class="flex items-center gap-3">
				<div
					class="gold-glow flex h-11 w-11 items-center justify-center rounded-xl border border-amber-500/30 bg-amber-500/20 text-amber-400 shadow-lg"
				>
					<RacingIcon name="trophy" size="lg" />
				</div>
				<div>
					<h1
						class="font-racing text-3xl font-black tracking-wide text-white uppercase italic sm:text-4xl"
					>
						CAMPIONATI GRAND PRIX
					</h1>
					<p class="mt-0.5 text-xs tracking-widest text-muted-foreground uppercase">
						Classifiche generali, gare in circuito e albi d'oro
					</p>
				</div>
			</div>

			{#if auth.isAdmin}
				<Button
					size="sm"
					class="heat-glow h-10 bg-primary px-5 font-racing text-base font-bold tracking-wider text-white uppercase transition-all hover:bg-accent"
					aria-label="Nuovo campionato"
					onclick={() => (newOpen = true)}
				>
					<RacingIcon name="flags" size="sm" class="mr-2" />
					Nuovo Campionato
				</Button>
			{/if}
		</div>
	</div>

	{#if error}
		<div
			class="flex items-center gap-2 rounded-xl border border-destructive/40 bg-destructive/15 p-3 text-xs text-red-300"
			role="alert"
		>
			<RacingIcon name="flame" size="xs" />
			<span>{error}</span>
		</div>
	{:else if !loaded}
		<div class="flex items-center justify-center p-12 text-muted-foreground">
			<RacingIcon name="speedometer" size="lg" class="mr-3 animate-spin text-primary" />
			<span class="font-racing text-lg tracking-wider uppercase"
				>Accesso alla griglia di partenza…</span
			>
		</div>
	{:else}
		<div class="space-y-5">
			{@render section('enrolled', 'I tuoi Campionati', groups.enrolled, 'helmet')}
			{@render section('active', 'Campionati Attivi', groups.active, 'flags')}
			{@render section('closed', 'Archivio Storico & Campionati Chiusi', groups.closed, 'trophy')}
		</div>
	{/if}

	{#if auth.isAdmin}
		<ChampionshipSettings
			championship={selected}
			bind:open={settingsOpen}
			onclosed={replaceChampionship}
			ondeleted={loadChampionships}
		/>
		<NewChampionshipDialog bind:open={newOpen} oncreated={loadChampionships} />
	{/if}
</main>
