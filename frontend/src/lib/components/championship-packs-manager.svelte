<script lang="ts">
	import { onMount } from 'svelte';
	import {
		createChampionshipPack,
		deleteChampionshipPack,
		listChampionshipPacks,
		updateChampionshipPack,
		type ChampionshipPack
	} from '$lib/championship-packs-api';
	import { listPackTemplates } from '$lib/shop-admin-api';
	import { errorMessage } from '$lib/shop-admin-format';
	import { emptyPackForm, formFromPack } from '$lib/shop-admin-validation';
	import type { PackData, PackTemplate } from '$lib/shop-admin-types';
	import PackCard from '$lib/components/pack-card.svelte';
	import PackForm from '$lib/components/pack-form.svelte';
	import { Button } from '$lib/components/ui/button';

	// Pacchetti del negozio di un campionato: elenco, "Crea pack" (da zero o da un template),
	// modifica ed eliminazione. A campionato chiuso resta in sola lettura.
	// `onchange` viene chiamato dopo ogni modifica, per aggiornare il negozio sullo sfondo.
	let {
		championshipId,
		closed,
		onchange
	}: {
		championshipId: number;
		closed: boolean;
		onchange?: () => void | Promise<void>;
	} = $props();

	const field = 'h-8 w-full rounded-md border border-input bg-background px-2 text-sm';

	let packs = $state<ChampionshipPack[]>([]);
	let templates = $state<PackTemplate[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let formOpen = $state(false);
	let editing = $state<ChampionshipPack | null>(null);
	let templateId = $state('');

	// Valori di partenza del modulo: il pacchetto in modifica, il template scelto o un modulo vuoto.
	let initial = $derived.by(() => {
		if (editing) return formFromPack(editing);
		const template = templates.find((item) => String(item.id) === templateId);
		return template ? formFromPack(template) : emptyPackForm();
	});

	async function reload() {
		packs = await listChampionshipPacks(championshipId);
		await onchange?.();
	}

	function create() {
		editing = null;
		templateId = '';
		formOpen = true;
	}

	function edit(item: ChampionshipPack) {
		editing = item;
		formOpen = true;
	}

	// Salva il pacchetto; un errore risale al modulo, che lo mostra.
	async function save(data: PackData) {
		if (editing) await updateChampionshipPack(championshipId, editing.id, data);
		else await createChampionshipPack(championshipId, data);
		formOpen = false;
		await reload();
	}

	async function remove(packId: number) {
		error = null;
		try {
			await deleteChampionshipPack(championshipId, packId);
			await reload();
		} catch (e) {
			error = errorMessage(e);
		}
	}

	onMount(async () => {
		try {
			[packs, templates] = await Promise.all([
				listChampionshipPacks(championshipId),
				listPackTemplates()
			]);
		} catch (e) {
			error = errorMessage(e);
		} finally {
			loading = false;
		}
	});
</script>

<div class="space-y-4">
	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{/if}

	{#if formOpen}
		<div class="space-y-3">
			<h3 class="font-semibold">{editing ? 'Modifica pacchetto' : 'Nuovo pacchetto'}</h3>
			{#if !editing}
				<label class="block space-y-1 text-sm">
					<span>Parti da un template</span>
					<select class={field} bind:value={templateId}>
						<option value="">Da zero</option>
						{#each templates as item (item.id)}
							<option value={String(item.id)}>{item.name}</option>
						{/each}
					</select>
				</label>
			{/if}
			{#key templateId}
				<PackForm
					{initial}
					submitLabel={editing ? 'Salva' : 'Crea'}
					onsubmit={save}
					oncancel={() => (formOpen = false)}
				/>
			{/key}
		</div>
	{:else}
		<div class="flex items-center justify-between gap-3">
			<p class="text-sm text-muted-foreground">
				{closed ? 'Campionato chiuso: pacchetti in sola lettura.' : `${packs.length} pacchetti`}
			</p>
			{#if !closed}
				<Button size="sm" onclick={create}>Crea pack</Button>
			{/if}
		</div>

		{#if loading}
			<p class="text-muted-foreground">Caricamento…</p>
		{:else if packs.length === 0}
			<p class="text-sm text-muted-foreground">Nessun pacchetto in questo negozio.</p>
		{:else}
			<ul class="grid gap-3 sm:grid-cols-2">
				{#each packs as item (item.id)}
					<PackCard
						pack={item}
						locked={closed}
						onedit={() => edit(item)}
						ondelete={() => remove(item.id)}
					/>
				{/each}
			</ul>
		{/if}
	{/if}
</div>
