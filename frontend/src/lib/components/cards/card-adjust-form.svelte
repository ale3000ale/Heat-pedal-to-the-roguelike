<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import type { PilotPlays } from '$lib/race/race-review-types';

	// Modulo del revisore per dare (bonus) o togliere (rimozione) una carta a un pilota.
	let {
		pilots,
		busy,
		onBonus,
		onRemove
	}: {
		pilots: PilotPlays[];
		busy: boolean;
		onBonus: (pilotId: number, cardName: string) => Promise<boolean>;
		onRemove: (pilotId: number, cardName: string) => Promise<boolean>;
	} = $props();

	let pilotId = $state<number | null>(null);
	let cardName = $state('');

	const fieldClass =
		'h-8 rounded-md border border-input bg-background px-2 text-sm disabled:opacity-50';

	let ready = $derived(pilotId !== null && cardName.trim().length > 0);

	// Esegue l'azione scelta e svuota il nome della carta solo se è andata a buon fine.
	async function submit(action: (id: number, name: string) => Promise<boolean>) {
		if (pilotId === null || !ready) return;
		if (await action(pilotId, cardName.trim())) cardName = '';
	}
</script>

<form class="flex flex-wrap items-end gap-3" onsubmit={(e) => e.preventDefault()}>
	<label class="flex flex-col gap-1 text-sm text-muted-foreground">
		Pilota
		<select class={fieldClass} bind:value={pilotId}>
			<option value={null}>Scegli…</option>
			{#each pilots as pilot (pilot.pilot_id)}
				<option value={pilot.pilot_id}>{pilot.pilot_name}</option>
			{/each}
		</select>
	</label>
	<label class="flex flex-col gap-1 text-sm text-muted-foreground">
		Nome della carta
		<input class={fieldClass} type="text" bind:value={cardName} />
	</label>
	<Button type="button" size="sm" disabled={busy || !ready} onclick={() => submit(onBonus)}>
		Dai bonus
	</Button>
	<Button
		type="button"
		size="sm"
		variant="outline"
		disabled={busy || !ready}
		onclick={() => submit(onRemove)}
	>
		Togli carta
	</Button>
</form>
