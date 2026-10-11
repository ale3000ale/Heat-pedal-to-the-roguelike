<script lang="ts">
	import { onMount } from 'svelte';
	import {
		createPackTemplate,
		deletePackTemplate,
		listPackTemplates,
		updatePackTemplate
	} from '$lib/shop-admin-api';
	import { errorMessage, packSummary } from '$lib/shop-admin-format';
	import { emptyPackForm, formFromPack } from '$lib/shop-admin-validation';
	import { packImageUrl } from '$lib/shop-cards';
	import type { PackData, PackTemplate } from '$lib/shop-admin-types';
	import ConfirmDialog from '$lib/components/confirm-dialog.svelte';
	import Modal from '$lib/components/modal.svelte';
	import PackForm from '$lib/components/pack-form.svelte';
	import { Button } from '$lib/components/ui/button';

	// Scheda "Template di pacchetto": elenco, creazione, modifica ed eliminazione.
	let templates = $state<PackTemplate[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let formOpen = $state(false);
	let editing = $state<PackTemplate | null>(null);
	let deleting = $state<PackTemplate | null>(null);
	let confirmOpen = $state(false);

	let initial = $derived(editing ? formFromPack(editing) : emptyPackForm());

	async function reload() {
		templates = await listPackTemplates();
	}

	function create() {
		editing = null;
		formOpen = true;
	}

	function edit(item: PackTemplate) {
		editing = item;
		formOpen = true;
	}

	function ask(item: PackTemplate) {
		deleting = item;
		confirmOpen = true;
	}

	// Salva il template; un errore risale al modulo, che lo mostra.
	async function save(data: PackData) {
		if (editing) await updatePackTemplate(editing.id, data);
		else await createPackTemplate(data);
		formOpen = false;
		await reload();
	}

	async function remove() {
		if (!deleting) return;
		error = null;
		try {
			await deletePackTemplate(deleting.id);
			await reload();
		} catch (e) {
			error = errorMessage(e);
		}
	}

	onMount(async () => {
		try {
			await reload();
		} catch (e) {
			error = errorMessage(e);
		} finally {
			loading = false;
		}
	});
</script>

<section class="space-y-4">
	<div class="flex items-center justify-between gap-3">
		<h2 class="text-lg font-semibold">Template di pacchetto</h2>
		<Button size="sm" onclick={create}>Nuovo template</Button>
	</div>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{/if}

	{#if loading}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else if templates.length === 0}
		<p class="text-sm text-muted-foreground">Nessun template di pacchetto.</p>
	{:else}
		<ul class="grid gap-3 sm:grid-cols-2">
			{#each templates as item (item.id)}
				<li class="flex gap-3 rounded-lg border bg-card p-3">
					<img
						src={packImageUrl(item.image_path)}
						alt={item.name}
						loading="lazy"
						class="h-24 w-16 rounded object-cover"
					/>
					<div class="flex flex-1 flex-col gap-1">
						<span class="font-medium">{item.name}</span>
						<span class="text-sm text-muted-foreground">{packSummary(item)}</span>
						{#if item.filter_enabled && item.filter_text}
							<span class="text-xs text-muted-foreground">Filtro: {item.filter_text}</span>
						{/if}
						<div class="mt-auto flex gap-2">
							<Button size="sm" variant="outline" onclick={() => edit(item)}>Modifica</Button>
							<Button size="sm" variant="destructive" onclick={() => ask(item)}>Elimina</Button>
						</div>
					</div>
				</li>
			{/each}
		</ul>
	{/if}
</section>

<Modal bind:open={formOpen} title={editing ? 'Modifica template' : 'Nuovo template'}>
	{#if formOpen}
		<PackForm
			{initial}
			submitLabel={editing ? 'Salva' : 'Crea'}
			onsubmit={save}
			oncancel={() => (formOpen = false)}
		/>
	{/if}
</Modal>

<ConfirmDialog
	bind:open={confirmOpen}
	title="Eliminare il template?"
	message={deleting
		? `Il template "${deleting.name}" viene tolto anche dai template di negozio.`
		: ''}
	confirmLabel="Elimina"
	onconfirm={remove}
/>
