<script lang="ts">
	import { onMount, untrack } from 'svelte';
	import { listPackImages, uploadPackImage } from '$lib/shop-admin-api';
	import { errorMessage } from '$lib/shop-admin-format';
	import { toPackData, validatePackForm, type PackForm } from '$lib/shop-admin-validation';
	import { packImageUrl } from '$lib/shop-cards';
	import type { PackData, PackImage } from '$lib/shop-admin-types';
	import { Button } from '$lib/components/ui/button';

	// Modulo di un pacchetto, usato per i template e per i pacchetti del campionato.
	// `onsubmit` esegue il salvataggio: se lancia un errore, il messaggio resta nel modulo.
	let {
		initial,
		submitLabel,
		onsubmit,
		oncancel
	}: {
		initial: PackForm;
		submitLabel: string;
		onsubmit: (data: PackData) => void | Promise<void>;
		oncancel: () => void;
	} = $props();

	const field = 'h-8 w-full rounded-md border border-input bg-background px-2 text-sm';

	let form = $state<PackForm>(untrack(() => ({ ...initial })));
	let images = $state<PackImage[]>([]);
	let error = $state<string | null>(null);
	let busy = $state(false);
	let uploading = $state(false);

	onMount(async () => {
		try {
			images = await listPackImages();
		} catch (e) {
			error = errorMessage(e);
		}
	});

	// Carica il file scelto e lo seleziona come immagine del pacchetto.
	async function pickFile(event: Event) {
		const input = event.currentTarget as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;
		error = null;
		uploading = true;
		try {
			const uploaded = await uploadPackImage(file);
			if (!images.some((image) => image.path === uploaded.path)) {
				images = [...images, uploaded];
			}
			form.image_path = uploaded.path;
		} catch (e) {
			error = errorMessage(e);
		} finally {
			uploading = false;
			input.value = '';
		}
	}

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		error = validatePackForm(form);
		if (error) return;
		busy = true;
		try {
			await onsubmit(toPackData(form));
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
		<input class={field} bind:value={form.name} maxlength="40" required />
	</label>

	<div class="grid grid-cols-2 gap-3">
		<label class="block space-y-1 text-sm">
			<span>Valuta</span>
			<select class={field} bind:value={form.currency}>
				<option value="gold">Oro</option>
				<option value="sponsor">Punti sponsor</option>
			</select>
		</label>
		<label class="block space-y-1 text-sm">
			<span>Costo</span>
			<input type="number" min="1" class={field} bind:value={form.cost} />
		</label>
		<label class="block space-y-1 text-sm">
			<span>Carte modifiche</span>
			<input type="number" min="0" class={field} bind:value={form.modifiche_count} />
		</label>
		<label class="block space-y-1 text-sm">
			<span>Carte sponsor</span>
			<input type="number" min="0" class={field} bind:value={form.sponsor_count} />
		</label>
	</div>

	<label class="flex items-center gap-2 text-sm">
		<input type="checkbox" bind:checked={form.filter_enabled} />
		Filtro per nome delle carte
	</label>
	<input
		class={field}
		bind:value={form.filter_text}
		disabled={!form.filter_enabled}
		placeholder="Nomi separati da virgola"
		aria-label="Nomi del filtro"
	/>

	<div class="space-y-2">
		<label class="block space-y-1 text-sm">
			<span>Immagine</span>
			<select class={field} bind:value={form.image_path}>
				<option value="">Immagine predefinita</option>
				{#each images as image (image.path)}
					<option value={image.path}>{image.path}</option>
				{/each}
			</select>
		</label>
		<input
			type="file"
			accept="image/png,image/jpeg,image/webp"
			onchange={pickFile}
			disabled={uploading}
			aria-label="Carica una nuova immagine"
			class="text-sm"
		/>
		{#if form.image_path}
			<img
				src={packImageUrl(form.image_path)}
				alt="Anteprima dell'immagine"
				class="h-24 w-16 rounded object-cover"
			/>
		{/if}
	</div>

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{/if}

	<div class="flex justify-end gap-2">
		<Button type="button" size="sm" variant="outline" onclick={oncancel}>Annulla</Button>
		<Button type="submit" size="sm" disabled={busy || uploading}>{submitLabel}</Button>
	</div>
</form>
