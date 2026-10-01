<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';

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

<main class="mx-auto max-w-sm p-6">
	<h1 class="text-2xl font-bold">Crea un account</h1>

	<form onsubmit={submit} class="mt-6 flex flex-col gap-4">
		<label class="flex flex-col gap-1 text-sm">
			Username
			<input
				bind:value={username}
				autocomplete="username"
				required
				class="rounded border border-neutral-700 bg-neutral-900 px-3 py-2"
			/>
		</label>

		<label class="flex flex-col gap-1 text-sm">
			Password
			<input
				type="password"
				bind:value={password}
				autocomplete="new-password"
				required
				class="rounded border border-neutral-700 bg-neutral-900 px-3 py-2"
			/>
		</label>

		<label class="flex flex-col gap-1 text-sm">
			Ripeti la password
			<input
				type="password"
				bind:value={confirm}
				autocomplete="new-password"
				required
				class="rounded border border-neutral-700 bg-neutral-900 px-3 py-2"
			/>
		</label>

		{#if error}
			<p class="text-sm text-red-400" role="alert">{error}</p>
		{/if}

		<button
			disabled={busy}
			class="rounded bg-red-600 px-4 py-2 font-semibold hover:bg-red-500 disabled:opacity-50"
		>
			{busy ? 'Creazione…' : 'Registrati'}
		</button>
	</form>

	<p class="mt-6 text-sm text-neutral-400">
		Hai già un account?
		<a href={resolve('/login')} class="text-red-400 underline">Accedi</a>
	</p>
</main>
