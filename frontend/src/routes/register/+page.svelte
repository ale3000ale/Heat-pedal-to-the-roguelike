<script lang="ts">
	import { goto } from '$app/navigation';
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';
	import * as Card from '$lib/components/ui/card';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import RacingIcon from '$lib/components/racing-icon.svelte';

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

<svelte:head>
	<title>Registra Scuderia — Heat Pedal to the Metal</title>
</svelte:head>

<main class="relative flex min-h-[92vh] items-center justify-center overflow-hidden p-4 sm:p-6">
	<!-- Cinematic Racing Background -->
	<div class="absolute inset-0 z-0">
		<img
			src="/images/heat-hero.jpg"
			alt="Heat Racing Background"
			class="h-full w-full object-cover object-center brightness-40 contrast-125 filter"
		/>
		<div
			class="absolute inset-0 bg-gradient-to-t from-[#0b0d13] via-[#0b0d13]/70 to-[#0b0d13]/80"
		></div>
	</div>

	<!-- Registration Card -->
	<div class="relative z-10 w-full max-w-md">
		<Card.Root
			class="overflow-hidden rounded-2xl border border-white/15 bg-[#121622]/95 shadow-2xl backdrop-blur-xl"
		>
			<!-- Kerb Trim at top -->
			<div class="curb-bar-thick" role="presentation"></div>

			<!-- Card Header -->
			<Card.Header class="pt-8 pb-4 text-center">
				<div
					class="gold-glow mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-2xl border border-amber-500/30 bg-amber-500/20 shadow-lg"
				>
					<RacingIcon name="helmet" size="xl" />
				</div>
				<Card.Title
					class="font-racing text-3xl font-black tracking-wider text-white uppercase italic sm:text-4xl"
				>
					REGISTRA <span class="text-amber-400">SCUDERIA</span>
				</Card.Title>
				<Card.Description
					class="mt-1 text-xs font-medium tracking-widest text-muted-foreground uppercase"
				>
					Crea la tua licenza per scendere in pista
				</Card.Description>
			</Card.Header>

			<Card.Content class="px-6 pb-8">
				<form onsubmit={submit} class="flex flex-col gap-4">
					<div class="flex flex-col gap-1.5">
						<Label
							for="username"
							class="font-racing text-xs tracking-wider text-muted-foreground uppercase"
						>
							Nome Pilota o Scuderia
						</Label>
						<Input
							id="username"
							bind:value={username}
							autocomplete="username"
							placeholder="es. Scuderia Rosso Corsa"
							class="h-11 rounded-lg border-white/10 bg-[#0d1017] px-4 text-sm text-white placeholder:text-muted-foreground/40 focus:border-primary focus:ring-primary"
							required
						/>
					</div>

					<div class="flex flex-col gap-1.5">
						<Label
							for="password"
							class="font-racing text-xs tracking-wider text-muted-foreground uppercase"
						>
							Password
						</Label>
						<Input
							id="password"
							type="password"
							bind:value={password}
							autocomplete="new-password"
							placeholder="Minimo 8 caratteri"
							class="h-11 rounded-lg border-white/10 bg-[#0d1017] px-4 text-sm text-white placeholder:text-muted-foreground/40 focus:border-primary focus:ring-primary"
							required
						/>
					</div>

					<div class="flex flex-col gap-1.5">
						<Label
							for="confirm"
							class="font-racing text-xs tracking-wider text-muted-foreground uppercase"
						>
							Conferma Password
						</Label>
						<Input
							id="confirm"
							type="password"
							bind:value={confirm}
							autocomplete="new-password"
							placeholder="Ripeti la password"
							class="h-11 rounded-lg border-white/10 bg-[#0d1017] px-4 text-sm text-white placeholder:text-muted-foreground/40 focus:border-primary focus:ring-primary"
							required
						/>
					</div>

					{#if error}
						<div
							class="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/15 px-3 py-2 text-xs text-red-300"
							role="alert"
						>
							<RacingIcon name="flame" size="xs" />
							<span>{error}</span>
						</div>
					{/if}

					<Button
						type="submit"
						disabled={busy}
						class="heat-glow mt-2 h-12 w-full bg-primary font-racing text-lg font-bold tracking-wider text-white uppercase transition-all hover:bg-accent disabled:opacity-50"
					>
						{#if busy}
							<RacingIcon name="speedometer" size="sm" class="mr-2 animate-spin" />
							<span>Registrazione in corso…</span>
						{:else}
							<RacingIcon name="flags" size="sm" class="mr-2" />
							<span>Firma la Licenza e Scendi in Pista</span>
						{/if}
					</Button>
				</form>

				<div class="mt-6 border-t border-white/10 pt-4 text-center">
					<p class="text-xs text-muted-foreground">
						Hai già una scuderia registrata?
						<a
							href={resolve('/login')}
							class="ml-1 font-bold text-amber-400 underline underline-offset-4 hover:text-amber-300"
						>
							Accedi al Paddock
						</a>
					</p>
				</div>
			</Card.Content>
		</Card.Root>
	</div>
</main>
