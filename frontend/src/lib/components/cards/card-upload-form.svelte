<script lang="ts">
	import { uploadCard, type UploadedCard } from '$lib/admin/card-admin-api';
	import type { PoolKind } from '$lib/types';
	import { Button } from '$lib/components/ui/button';
	import CardCropEditor from '$lib/components/cards/card-crop-editor.svelte';

	// Modulo per caricare una carta nella pool di base del tipo indicato.
	// onuploaded riceve la carta creata, così la pagina può ricaricare l'elenco.
	interface Props {
		kind: PoolKind;
		onuploaded: (card: UploadedCard) => void;
	}

	let { kind, onuploaded }: Props = $props();

	let name = $state('');
	let copies = $state(1);
	let file = $state<File | null>(null);
	let blob = $state<Blob | null>(null);
	let input = $state<HTMLInputElement>();
	let error = $state<string | null>(null);
	let busy = $state(false);

	function chooseFile(e: Event & { currentTarget: HTMLInputElement }) {
		file = e.currentTarget.files?.[0] ?? null;
	}

	// Riporta il modulo allo stato iniziale dopo un invio riuscito.
	function reset() {
		name = '';
		copies = 1;
		file = null;
		blob = null;
		if (input) input.value = '';
	}

	// Invia la carta. Errori del backend (nome già usato, file troppo grande, immagine non
	// valida) compaiono nel modulo.
	async function submit(event: SubmitEvent) {
		event.preventDefault();
		error = null;
		if (!blob) {
			error = "Scegli un'immagine e attendi che il ritaglio sia pronto";
			return;
		}
		if (!Number.isInteger(copies) || copies < 1) {
			error = 'Le copie devono essere un numero intero da 1 in su';
			return;
		}
		busy = true;
		try {
			const card = await uploadCard(kind, name.trim(), copies, blob);
			reset();
			onuploaded(card);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}
</script>

<form class="space-y-4" onsubmit={submit}>
	<label class="block space-y-1 text-sm">
		<span>Nome della carta</span>
		<input
			class="h-9 w-full rounded-md border bg-background px-3 text-sm"
			bind:value={name}
			required
		/>
	</label>

	<label class="block space-y-1 text-sm">
		<span>Copie</span>
		<input
			type="number"
			class="h-9 w-20 rounded-md border bg-background px-2 text-sm"
			min={1}
			bind:value={copies}
			required
		/>
	</label>

	<label class="block space-y-1 text-sm">
		<span>Immagine</span>
		<input
			type="file"
			accept="image/*"
			class="block w-full text-sm"
			bind:this={input}
			onchange={chooseFile}
		/>
	</label>

	{#if file}
		<CardCropEditor {file} bind:blob />
	{/if}

	{#if error}
		<p class="text-sm text-destructive" role="alert">{error}</p>
	{/if}
	<Button type="submit" disabled={busy || !blob}>Carica carta</Button>
</form>
