<script lang="ts">
	import { api } from '$lib/api';
	import { listShopTemplates } from '$lib/shop-admin-api';
	import { Button } from '$lib/components/ui/button';
	import Modal from '$lib/components/modal.svelte';
	import type { ShopTemplate } from '$lib/shop-admin-types';
	import type { Pool } from '$lib/types';

	let {
		open = $bindable(false),
		oncreated
	}: { open?: boolean; oncreated?: () => void | Promise<void> } = $props();

	const fieldClass = 'h-9 w-full rounded-md border border-input bg-background px-3 text-sm';

	let pools = $state<Pool[]>([]);
	let shopTemplates = $state<ShopTemplate[]>([]);
	let name = $state('');
	let poolId = $state('');
	let sponsorId = $state('');
	let shopTemplateId = $state('');
	let error = $state<string | null>(null);
	let busy = $state(false);
	let poolsLoaded = false;

	let modifichePools = $derived(pools.filter((pool) => pool.kind === 'modifiche'));
	let sponsorPools = $derived(pools.filter((pool) => pool.kind === 'sponsor'));

	function message(e: unknown): string {
		return e instanceof Error ? e.message : 'Errore sconosciuto';
	}

	function describe(pool: Pool): string {
		return `${pool.name} (${pool.cards_count} carte, ${pool.copies_count} copie)`;
	}

	// Un template di negozio senza pacchetti non si può scegliere.
	function shopLabel(item: ShopTemplate): string {
		return item.is_empty ? `${item.name} (senza pacchetti)` : item.name;
	}

	// Preseleziona la pool di base di ciascun tipo.
	function presetPools() {
		const base = modifichePools.find((pool) => pool.name === 'default') ?? modifichePools[0];
		poolId = base ? String(base.id) : '';
		const sponsor = sponsorPools.find((pool) => pool.name === 'sponsor') ?? sponsorPools[0];
		sponsorId = sponsor ? String(sponsor.id) : '';
	}

	// Le pool si caricano una volta sola; i template di negozio a ogni apertura,
	// perché l'admin può averne creati nel frattempo. Il negozio parte vuoto di default.
	async function prepare() {
		error = null;
		try {
			if (!poolsLoaded) {
				pools = await api<Pool[]>('/pools');
				poolsLoaded = true;
				presetPools();
			}
			shopTemplates = await listShopTemplates();
			const chosen = shopTemplates.find((item) => String(item.id) === shopTemplateId);
			if (!chosen || chosen.is_empty) shopTemplateId = '';
		} catch (e) {
			error = message(e);
		}
	}

	$effect(() => {
		if (open) prepare();
	});

	async function create(event: SubmitEvent) {
		event.preventDefault();
		error = null;
		busy = true;
		try {
			await api('/championships', {
				method: 'POST',
				body: {
					name,
					pool_id: poolId ? Number(poolId) : null,
					sponsor_pool_id: sponsorId ? Number(sponsorId) : null,
					shop_template_id: shopTemplateId ? Number(shopTemplateId) : null
				}
			});
			name = '';
			shopTemplateId = '';
			open = false;
			await oncreated?.();
		} catch (e) {
			error = message(e);
		} finally {
			busy = false;
		}
	}
</script>

<Modal bind:open title="Nuovo campionato">
	<form class="space-y-4" onsubmit={create}>
		<p class="text-sm text-muted-foreground">
			Ogni campionato riceve una copia indipendente delle due pool scelte.
		</p>

		<label class="block space-y-1 text-sm">
			<span>Nome</span>
			<input class={fieldClass} bind:value={name} minlength={2} maxlength={40} required />
		</label>

		<label class="block space-y-1 text-sm">
			<span>Pool delle modifiche</span>
			<select class={fieldClass} bind:value={poolId}>
				{#each modifichePools as pool (pool.id)}
					<option value={String(pool.id)}>{describe(pool)}</option>
				{/each}
			</select>
		</label>

		<label class="block space-y-1 text-sm">
			<span>Pool degli sponsor</span>
			<select class={fieldClass} bind:value={sponsorId}>
				<option value="">Nessuna</option>
				{#each sponsorPools as pool (pool.id)}
					<option value={String(pool.id)}>{describe(pool)}</option>
				{/each}
			</select>
		</label>

		<label class="block space-y-1 text-sm">
			<span>Template del negozio</span>
			<select class={fieldClass} bind:value={shopTemplateId}>
				<option value="">Negozio vuoto</option>
				{#each shopTemplates as item (item.id)}
					<option value={String(item.id)} disabled={item.is_empty}>{shopLabel(item)}</option>
				{/each}
			</select>
		</label>

		{#if error}
			<p class="text-sm text-destructive" role="alert">{error}</p>
		{/if}
		<Button type="submit" disabled={busy}>Crea campionato</Button>
	</form>
</Modal>
