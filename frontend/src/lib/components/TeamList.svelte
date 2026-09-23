<!-- frontend/src/lib/components/TeamList.svelte -->
<!-- Elenco team con relativi piloti ordinati per punteggio, evidenziando il pilota dell'utente. -->
<script lang="ts">
	export let teams: {
		id: number;
		name: string;
		total_points: number;
		pilots: { id: number; name: string; point: number; is_current_user_pilot: boolean }[];
	}[];
</script>

<div class="space-y-6">
	{#each teams as team}
		<div class="app-card">
			<div class="flex justify-between items-baseline mb-3">
				<h3 class="font-display font-semibold text-lg">{team.name}</h3>
				<span class="text-sm opacity-70">Totale: {team.total_points} pt</span>
			</div>
			<ul class="space-y-1">
				{#each team.pilots as pilot}
					<li>
						<a
							href={`/piloti/${pilot.id}`}
							class="flex justify-between rounded px-2 py-1 hover:bg-racing-black/5 dark:hover:bg-white/10
								{pilot.is_current_user_pilot ? 'app-card--highlight' : ''}"
						>
							<span>{pilot.name}</span>
							<span class="font-semibold">{pilot.point} pt</span>
						</a>
					</li>
				{/each}
			</ul>
		</div>
	{/each}

	{#if teams.length === 0}
		<p class="text-sm opacity-70">Nessun team disponibile.</p>
	{/if}
</div>
