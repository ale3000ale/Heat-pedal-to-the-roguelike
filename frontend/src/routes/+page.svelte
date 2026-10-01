<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';

	// Se non c'è nessun utente loggato rimanda alla pagina di login.
	// Gira anche dopo il logout: lo stato si svuota e l'effetto scatta da solo.
	$effect(() => {
		if (auth.ready && !auth.user) goto(resolve('/login'));
	});

	// Esce dall'account (il redirect lo fa l'effetto qui sopra).
	async function logout() {
		await auth.logout().catch(() => {});
	}
</script>

<svelte:head><title>Heat</title></svelte:head>

{#if auth.user}
	<main class="mx-auto max-w-2xl p-6">
		<h1 class="text-3xl font-bold">Heat: Pedal to the Roguelike</h1>
		<p class="mt-4 text-neutral-300">
			Ciao <strong>{auth.user.username}</strong>
			<span class="ml-2 rounded bg-neutral-800 px-2 py-0.5 text-xs uppercase">
				{auth.user.role}
			</span>
		</p>
		<button onclick={logout} class="mt-6 rounded bg-neutral-800 px-4 py-2 hover:bg-neutral-700">
			Esci
		</button>
	</main>
{/if}
