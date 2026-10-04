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
	let confirm = $state('');
	let error = $state<string | null>(null);
	let busy = $state(false);

	// Dopo la registrazione l'utente risulta già loggato: va alla home.
	$effect(() => {
		if (auth.user) goto(resolve('/'));
	});

	// Controlla che le due password coincidano, poi crea l'account.
	async function submit(event: SubmitEvent) {
		event.preventDefault();
		error = null;
		if (password !== confirm) {
			error = 'Le password non coincidono';
			return;
		}
		busy = true;
		try {
			await auth.register(username, password);
		} catch (e) {
			error = e instanceof Error ? e.message : 'Errore sconosciuto';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>Registrati - Heat</title></svelte:head>

<main class="mx-auto flex min-h-[80vh] max-w-sm items-center p-6">
	<Card.Root class="w-full">
		<Card.Header>
			<Card.Title class="text-2xl">Crea un account</Card.Title>
			<Card.Description>Scegli username e password per entrare in Heat.</Card.Description>
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
						autocomplete="new-password"
						required
					/>
				</div>

				<div class="flex flex-col gap-2">
					<Label for="confirm">Ripeti la password</Label>
					<Input
						id="confirm"
						type="password"
						bind:value={confirm}
						autocomplete="new-password"
						required
					/>
				</div>

				{#if error}
					<p class="text-sm text-destructive" role="alert">{error}</p>
				{/if}

				<Button type="submit" disabled={busy}>{busy ? 'Creazione…' : 'Registrati'}</Button>
			</form>

			<p class="mt-6 text-sm text-muted-foreground">
				Hai già un account?
				<a href={resolve('/login')} class="text-foreground underline">Accedi</a>
			</p>
		</Card.Content>
	</Card.Root>
</main>
