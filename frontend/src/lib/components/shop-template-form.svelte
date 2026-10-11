<script lang="ts">
	import { untrack } from 'svelte';
	import { errorMessage, packSummary } from '$lib/shop-admin-format';
	import { validateShopTemplate } from '$lib/shop-admin-validation';
	import type { PackTemplate, ShopTemplateData } from '$lib/shop-admin-types';
	import { Button } from '$lib/components/ui/button';

	// Modulo di un template di negozio: nome e scelta dei template di pacchetto.
	// In creazione serve almeno un pacchetto; in modifica l'elenco può essere vuoto.
	let {
		packTemplates,
		initialName,
		initialIds,
		requirePacks,
		submitLabel,
		onsubmit,
		oncancel
	}: {
		packTemplates: PackTemplate[];
		initialName: string;
		initialIds: number[];
		requirePacks: boolean;
		submitLabel: string;
		onsubmit: (data: ShopTemplateData) => void | Promise<void>;
		oncancel: () => void;
	} = $props();

	const field = 'h-8 w-full rounded-md border border-input bg-background px-2 text-sm';

	let name = $state(untrack(() => initialName));
	let selectedIds = $state<number[]>(untrack(() => [...initialIds]));
	let error = $state<string | null>(null);
	let busy = $state(false);

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		error = validateShopTemplate(name, selectedIds, requirePacks);
		if (error) return;
		busy = true;
		try {
			await onsubmit({ name: name.trim(), pack_template_ids: selectedIds });
		} catch (e) {
			error = errorMessage(e);
		} finally {
			busy = false;
		}
	}
</script>

<form onsubmit={submit} class="space-y-3">
	<label class="block space-y-1 text-sm">
		<span>Nome</span>
		<input class={field} bind:value={name} maxlength="40" required />
	</label>

	<fieldset class="space-y-1">
		<legend class="text-sm">Template di pacchetto</legend>
		{#if packTemplates.length === 0}
			<p class="text-sm text-muted-foreground">Crea prima un template di pacchetto.</p>
		{:else}
			{#each packTemplates as item (item.id)}
				<label class="flex items-center gap-2 text-sm">
					<input type="checkbox" value={item.id} bind:group={selectedIds} />
					{item.name} · {packSummary(item)}
				</label>
			{/each}
		{/if}
	</fieldset>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{/if}

	<div class="flex justify-end gap-2">
		<Button type="button" size="sm" variant="outline" onclick={oncancel}>Annulla</Button>
		<Button type="submit" size="sm" disabled={busy}>{submitLabel}</Button>
	</div>
</form>
