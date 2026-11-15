<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { draftAttendanceView } from '$lib/draft/attendance/draft-attendance-view';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	let { store, ondraft }: { store: DraftStore; ondraft: () => void } = $props();
	const view = $derived(draftAttendanceView(store.state));

	/** Cambia solo la schermata locale tramite il padre: non estrae carte o crea gare. */
	function chooseDraft(): void {
		store.syncContext();
		if (draftAttendanceView(store.state).canEdit) ondraft();
	}

	/** Il server crea la gara normale; nessun controllo client dei mazzi o READY. */
	async function alreadyDisputed(): Promise<void> {
		store.syncContext();
		if (!draftAttendanceView(store.state).canEdit) return;
		await store.command('already-disputed', {});
	}
</script>

{#if view.available}
	<section aria-label="Tipo di preparazione gara" aria-busy={store.busy} class="space-y-4">
		<p class="text-sm text-muted-foreground">Scegli come preparare la gara.</p>
		<div class="grid gap-3 sm:grid-cols-2">
			<Button type="button" disabled={!view.canEdit} onclick={chooseDraft}>Draft</Button>
			<Button type="button" variant="outline" disabled={!view.canEdit} onclick={alreadyDisputed}>
				Gara già disputata
			</Button>
		</div>
		<p class="text-sm text-muted-foreground">
			Draft prosegue con Presenti e Assenti. Gara già disputata crea una gara normale: i risultati
			saranno inseriti successivamente, senza draft o preparazione READY.
		</p>
		{#if store.busy}
			<p role="status" class="text-sm">Operazione in corso…</p>
		{/if}
	</section>
{:else}
	<p role="status" class="text-sm">Scelta iniziale non disponibile nello stato corrente.</p>
{/if}
