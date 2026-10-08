<script lang="ts">
	import { onMount } from 'svelte';
	import {
		createShopTemplate,
		deleteShopTemplate,
		listPackTemplates,
		listShopTemplates,
		updateShopTemplate
	} from '$lib/shop-admin-api';
	import { errorMessage } from '$lib/shop-admin-format';
	import type { PackTemplate, ShopTemplate, ShopTemplateData } from '$lib/shop-admin-types';
	import ConfirmDialog from '$lib/components/confirm-dialog.svelte';
	import Modal from '$lib/components/modal.svelte';
	import ShopTemplateForm from '$lib/components/shop-template-form.svelte';
	import { Button } from '$lib/components/ui/button';

	// Scheda "Template di negozio": un template senza pacchetti ha il triangolo giallo
	// e non è utilizzabile nella creazione del campionato.
	let shops = $state<ShopTemplate[]>([]);
	let packTemplates = $state<PackTemplate[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let formOpen = $state(false);
	let editing = $state<ShopTemplate | null>(null);
	let deleting = $state<ShopTemplate | null>(null);
	let confirmOpen = $state(false);

	let packNames = $derived(new Map(packTemplates.map((item) => [item.id, item.name])));

	async function reload() {
		[shops, packTemplates] = await Promise.all([listShopTemplates(), listPackTemplates()]);
	}

	// Nomi dei template di pacchetto di un template di negozio.
	function namesOf(item: ShopTemplate): string {
		return item.pack_template_ids.map((id) => packNames.get(id) ?? '?').join(', ');
	}

	function create() {
		editing = null;
		formOpen = true;
	}

	function edit(item: ShopTemplate) {
		editing = item;
		formOpen = true;
	}

	function ask(item: ShopTemplate) {
		deleting = item;
		confirmOpen = true;
	}

	// Salva il template; un errore risale al modulo, che lo mostra.
	async function save(data: ShopTemplateData) {
		if (editing) await updateShopTemplate(editing.id, data);
		else await createShopTemplate(data);
		formOpen = false;
		await reload();
	}

	async function remove() {
		if (!deleting) return;
		error = null;
		try {
			await deleteShopTemplate(deleting.id);
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
		<h2 class="text-lg font-semibold">Template di negozio</h2>
		<Button size="sm" onclick={create}>Nuovo template</Button>
	</div>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{/if}

	{#if loading}
		<p class="text-muted-foreground">Caricamento…</p>
	{:else if shops.length === 0}
		<p class="text-sm text-muted-foreground">Nessun template di negozio.</p>
	{:else}
		<ul class="space-y-2">
			{#each shops as item (item.id)}
				<li class="flex flex-wrap items-center gap-3 rounded-lg border bg-card p-3">
					<div class="flex flex-1 flex-col gap-1">
						<span class="font-medium">{item.name}</span>
						{#if item.is_empty}
							<span class="text-sm font-medium text-yellow-600">⚠ Senza pacchetti</span>
						{:else}
							<span class="text-sm text-muted-foreground">{namesOf(item)}</span>
						{/if}
					</div>
					<div class="flex gap-2">
						<Button size="sm" variant="outline" onclick={() => edit(item)}>Modifica</Button>
						<Button size="sm" variant="destructive" onclick={() => ask(item)}>Elimina</Button>
					</div>
				</li>
			{/each}
		</ul>
	{/if}
</section>

<Modal
	bind:open={formOpen}
	title={editing ? 'Modifica template di negozio' : 'Nuovo template di negozio'}
>
	{#if formOpen}
		<ShopTemplateForm
			{packTemplates}
			initialName={editing?.name ?? ''}
			initialIds={editing?.pack_template_ids ?? []}
			requirePacks={editing === null}
			submitLabel={editing ? 'Salva' : 'Crea'}
			onsubmit={save}
			oncancel={() => (formOpen = false)}
		/>
	{/if}
</Modal>

<ConfirmDialog
	bind:open={confirmOpen}
	title="Eliminare il template di negozio?"
	message={deleting
		? `Il template "${deleting.name}" viene eliminato; i pacchetti restano.`
		: ''}
	confirmLabel="Elimina"
	onconfirm={remove}
/>
