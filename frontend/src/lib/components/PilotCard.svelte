<!-- frontend/src/lib/components/PilotCard.svelte -->
<!-- Card riutilizzabile per mostrare i dati sintetici di un pilota (Home, liste, team). -->
<script lang="ts">
	export let pilot: { id: number; name: string; point: number; team_name?: string | null };
	export let championshipName: string = '';
	export let highlight: boolean = false; // true se e' il pilota dell'utente loggato (Team page)
</script>

<a href={`/piloti/${pilot.id}`} class="app-card block {highlight ? 'app-card--highlight' : ''}">
	<div class="flex items-center justify-between">
		<h3 class="font-display font-semibold text-lg">{pilot.name}</h3>
		<span class="rounded-full bg-racing-gold/20 px-2 py-0.5 text-sm font-semibold text-racing-gold">
			{pilot.point} pt
		</span>
	</div>
	{#if pilot.team_name}
		<p class="text-sm opacity-70 mt-1">Team: {pilot.team_name}</p>
	{/if}
	{#if championshipName}
		<p class="text-sm opacity-70 mt-1">Campionato: {championshipName}</p>
	{/if}
</a>
