<!-- frontend/src/lib/components/PilotList.svelte -->
<!-- Elenco piloti in ordine alfabetico, con team e campionato associati (riutilizzato con/senza login). -->
<script lang="ts">
	export let pilots: {
		id: number;
		name: string;
		team_name?: string | null;
		championship_name?: string | null;
		point: number;
	}[];
	export let emptyMessage: string = 'Nessun pilota trovato.';
</script>

<ul class="space-y-2">
	{#each pilots as pilot}
		<li>
			<a
				href={`/piloti/${pilot.id}`}
				class="app-card flex justify-between items-center hover:shadow-md"
			>
				<div>
					<p class="font-semibold">{pilot.name}</p>
					<p class="text-sm opacity-70">
						{pilot.team_name ? `Team: ${pilot.team_name}` : 'Senza team'}
						{#if pilot.championship_name} · {pilot.championship_name}{/if}
					</p>
				</div>
				<span class="font-semibold">{pilot.point} pt</span>
			</a>
		</li>
	{/each}

	{#if pilots.length === 0}
		<p class="text-sm opacity-70">{emptyMessage}</p>
	{/if}
</ul>
