<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import { draftAttendanceView, MAX_DRAFT_PRESENT } from '$lib/draft-attendance-view';
	import type { DraftStore } from '$lib/stores/draft.svelte';

	let { store }: { store: DraftStore } = $props();
	const view = $derived(draftAttendanceView(store.state));

	/** Ricontrolla il pilota nello snapshot corrente e attende il server prima di spostarlo. */
	async function setPresent(pilotId: number, present: boolean): Promise<void> {
		store.syncContext();
		const state = store.state;
		if (!draftAttendanceView(state).canEdit) return;
		const pilot = state.snapshot?.participants.find((item) => item.pilot_id === pilotId);
		if (!pilot || pilot.present === present) return;
		await store.command('attendance', { pilot_id: pilotId, present });
	}

	/** Il backend decide ordine oppure mazzi e applica i controlli preliminari previsti. */
	async function next(): Promise<void> {
		store.syncContext();
		if (!draftAttendanceView(store.state).canContinue) return;
		await store.command('attendance/confirm', {});
	}
</script>

{#if view.available}
	<section aria-label="Presenze gara" aria-busy={store.busy} class="space-y-5">
		<section aria-label="Piloti presenti" class="space-y-2">
			<h3 class="font-semibold">Presenti ({view.count})</h3>
			{#if view.present.length === 0}
				<p class="text-sm text-muted-foreground">Nessun pilota presente.</p>
			{:else}
				<ul class="space-y-2">
					{#each view.present as pilot (pilot.pilot_id)}
						<li class="flex items-center justify-between gap-3 rounded-md border p-3">
							<span class="min-w-0 break-words">{pilot.name}</span>
							<Button
								type="button"
								size="sm"
								variant="outline"
								disabled={!view.canEdit}
								aria-label={`Escludi ${pilot.name}`}
								onclick={() => setPresent(pilot.pilot_id, false)}>Escludi</Button
							>
						</li>
					{/each}
				</ul>
			{/if}
		</section>
		<section aria-label="Piloti assenti" class="space-y-2">
			<h3 class="font-semibold">Assenti ({view.absent.length})</h3>
			{#if view.absent.length === 0}
				<p class="text-sm text-muted-foreground">Nessun pilota assente.</p>
			{:else}
				<ul class="space-y-2">
					{#each view.absent as pilot (pilot.pilot_id)}
						<li class="flex items-center justify-between gap-3 rounded-md border p-3">
							<span class="min-w-0 break-words">{pilot.name}</span>
							<Button
								type="button"
								size="sm"
								variant="outline"
								disabled={!view.canEdit}
								aria-label={`Includi ${pilot.name}`}
								onclick={() => setPresent(pilot.pilot_id, true)}>Includi</Button
							>
						</li>
					{/each}
				</ul>
			{/if}
		</section>
		{#if view.count < 1 || view.count > MAX_DRAFT_PRESENT}
			<p role="status" class="text-sm">Servono da 1 a {MAX_DRAFT_PRESENT} piloti presenti.</p>
		{/if}
		<div class="flex justify-end">
			<Button type="button" disabled={!view.canContinue} onclick={next}>Avanti</Button>
		</div>
	</section>
{:else}
	<p role="status" class="text-sm">Selezione presenze non disponibile nello stato corrente.</p>
{/if}
