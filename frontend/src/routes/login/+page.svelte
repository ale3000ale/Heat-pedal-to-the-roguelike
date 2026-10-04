<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

	let username = $state('');
	let password = $state('');
	let error = $state<string | null>(null);
	let busy = $state(false);

	// Chi è già loggato (anche appena dopo il login) viene portato alla home.
	$effect(() => {
		if (auth.user) goto(resolve('/'));
	});

	// Invia le credenziali; se sono sbagliate mostra il messaggio del backend.
	async function submit(event: SubmitEvent) {
		event.preventDefault();
		error = null;
		busy = true;
		try {
			await auth.login(username, password);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>Accedi - Heat</title></svelte:head>

<main class="mx-auto flex min-h-[80vh] max-w-sm items-center p-6">
	<Card.Root class="w-full">
		<Card.Header>
			<Card.Title class="text-2xl">Accedi</Card.Title>
			<Card.Description>Entra nel tuo account Heat.</Card.Description>
		</Card.Header>
		<Card.Content>
			<form onsubmit={submit} class="flex flex-col gap-4">
				<div class="flex flex-col gap-2">
					<Label for="username">Username</Label>
					<Input id="username" bind:value={username} autocomplete="username" required />
				</div>

				<div class="flex flex-col gap-2">
					<Label for="password">Password</Label>
					<Input
						id="password"
						type="password"
						bind:value={password}
						autocomplete="current-password"
						required
					/>
				</div>

				{#if error}
					<p class="text-sm text-destructive" role="alert">{error}</p>
				{/if}

				<Button type="submit" disabled={busy}>{busy ? 'Accesso…' : 'Entra'}</Button>
			</form>

			<p class="mt-6 text-sm text-muted-foreground">
				Non hai un account?
				<a href={resolve('/register')} class="text-foreground underline">Registrati</a>
			</p>
		</Card.Content>
	</Card.Root>
</main>
