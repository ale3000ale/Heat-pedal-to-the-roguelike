<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import type { PilotPlays } from '$lib/race/race-review-types';

	// Giocate di un pilota con il tasto per annullarle (solo a revisione attiva).
	let {
		pilot,
		canCancel,
		busy,
		onCancel
	}: {
		pilot: PilotPlays;
		canCancel: boolean;
		busy: boolean;
		onCancel: (playId: number) => void;
	} = $props();
</script>

<div class="space-y-2">
	<h3 class="text-sm font-semibold">{pilot.pilot_name}</h3>
	{#if pilot.plays.length === 0}
		<p class="text-sm text-muted-foreground">Nessuna carta giocata.</p>
	{:else}
		<ul class="flex flex-wrap gap-3">
			{#each pilot.plays as play (play.id)}
				<li class="flex w-28 flex-col items-center gap-1 text-center">
					<img
						src="/media/{play.card_path}"
						alt={play.card_name}
						width="96"
						height="134"
						loading="lazy"
						class="h-auto w-24 rounded-md border"
					/>
					<span class="text-xs font-medium">{play.card_name}</span>
					<span class="text-xs text-muted-foreground">{play.status}</span>
					{#if canCancel}
						<Button
							type="button"
							size="sm"
							variant="outline"
							disabled={busy}
							onclick={() => onCancel(play.id)}
							aria-label={`Annulla ${play.card_name} di ${pilot.pilot_name}`}
						>
							Annulla
						</Button>
					{/if}
				</li>
			{/each}
		</ul>
	{/if}
</div>
