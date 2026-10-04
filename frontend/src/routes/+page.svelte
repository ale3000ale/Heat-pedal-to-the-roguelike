<script lang="ts">
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';
	import * as Card from '$lib/components/ui/card';
</script>

<svelte:head><title>Heat</title></svelte:head>

<main class="mx-auto max-w-5xl p-6">
	{#if auth.user}
		<h1 class="text-2xl font-bold">Ciao, {auth.user.username}</h1>
		<p class="mt-1 text-muted-foreground">
			{auth.isAdmin ? 'Sei amministratore.' : 'Benvenuto nel campionato.'}
		</p>

		<div class="mt-6 grid gap-4 sm:grid-cols-2">
			<a href={resolve('/team')}>
				<Card.Root class="transition-colors hover:bg-accent">
					<Card.Header>
						<Card.Title>I tuoi team e piloti</Card.Title>
						<Card.Description>Crea e gestisci team e piloti.</Card.Description>
					</Card.Header>
				</Card.Root>
			</a>
			<Card.Root>
				<Card.Header>
					<Card.Title>Campionati</Card.Title>
					<Card.Description>In arrivo.</Card.Description>
				</Card.Header>
			</Card.Root>
		</div>
	{/if}
</main>
