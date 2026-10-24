<script lang="ts">
	import { resolve } from '$app/paths';
	import { auth } from '$lib/auth.svelte';
	import RacingIcon from '$lib/components/racing-icon.svelte';
	import { Button } from '$lib/components/ui/button';
</script>

<svelte:head>
	<title>Paddock — Heat Pedal to the Roguelike</title>
</svelte:head>

<main class="mx-auto max-w-6xl px-4 py-8 sm:px-6">
	{#if auth.user}
		<!-- Hero Grand Prix Banner -->
		<div class="relative overflow-hidden rounded-2xl border border-white/10 bg-[#121620] shadow-2xl mb-8 group">
			<!-- Background artwork with dark gradient overlay -->
			<div class="absolute inset-0 z-0">
				<img
					src="/images/heat-hero.jpg"
					alt="Heat Grand Prix Racing"
					class="h-full w-full object-cover object-center opacity-25 transition-transform duration-700 ease-out group-hover:scale-105"
				/>
				<div class="absolute inset-0 bg-gradient-to-r from-[#0d1017] via-[#0d1017]/85 to-[#0d1017]/20"></div>
				<div class="absolute inset-0 bg-gradient-to-t from-[#0d1017] via-transparent to-transparent"></div>
			</div>

			<!-- Signature Kerb Accent at the top of banner -->
			<div class="curb-bar relative z-10" role="presentation"></div>

			<!-- Hero Content -->
			<div class="relative z-10 p-6 sm:p-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
				<div class="max-w-xl">
					<div class="flex items-center gap-2 mb-3">
						<span class="inline-flex items-center gap-1.5 rounded-full bg-primary/20 px-3 py-1 text-xs font-bold uppercase tracking-wider text-primary border border-primary/30">
							<RacingIcon name="flame" size="xs" />
							Stagione Grand Prix Attiva
						</span>
						{#if auth.isAdmin}
							<span class="inline-flex items-center gap-1 rounded-full bg-amber-500/20 px-3 py-1 text-xs font-bold uppercase tracking-wider text-amber-300 border border-amber-500/30">
								<RacingIcon name="wrenches" size="xs" />
								Pannello Direzione Gara
							</span>
						{/if}
					</div>

					<h1 class="font-racing text-4xl sm:text-5xl font-black italic tracking-wide uppercase text-white leading-tight">
						BENVENUTO NEL PADDOCK, <span class="text-heat">{auth.user.username}</span>
					</h1>

					<p class="mt-3 text-sm sm:text-base text-muted-foreground leading-relaxed">
						Prepara i bolidi della tua scuderia, calcola il calore del motore nelle staccate al limite e taglia il traguardo per primo.
					</p>

					<div class="mt-6 flex flex-wrap items-center gap-3">
						<a href={resolve('/team')}>
							<Button class="bg-primary hover:bg-accent text-white font-racing tracking-wider uppercase font-bold text-base px-6 h-11 heat-glow transition-all">
								<RacingIcon name="helmet" size="sm" class="mr-2" />
								Gestisci Scuderia
							</Button>
						</a>
						<a href={resolve('/championships')}>
							<Button variant="outline" class="border-white/20 bg-black/40 hover:bg-white/10 text-white font-racing tracking-wider uppercase font-bold text-base px-6 h-11 transition-all">
								<RacingIcon name="flags" size="sm" class="mr-2" />
								Griglia Campionati
							</Button>
						</a>
					</div>
				</div>

				<!-- Right side: pilot artwork + telemetry HUD -->
				<div class="hidden lg:flex flex-col gap-4 shrink-0">
					<!-- Official game pilot artwork -->
					<div class="relative w-52 h-52 rounded-2xl overflow-hidden border border-white/15 shadow-2xl">
						<img
							src="/images/heat-pilot-green.jpg"
							alt="Heat Pilota — Illustrazione Ufficiale"
							class="w-full h-full object-cover object-top transition-transform duration-700 group-hover:scale-105"
						/>
						<div class="absolute inset-0 bg-gradient-to-t from-[#0d1017]/90 via-transparent to-transparent"></div>
						<div class="absolute bottom-2 left-3 right-3">
							<span class="font-racing text-xs uppercase tracking-wider text-amber-400 font-bold">Heat — Pedal to the Metal</span>
						</div>
					</div>

					<!-- Telemetry Quick HUD -->
					<div class="flex flex-col gap-2.5 rounded-xl border border-white/10 bg-[#0e121a]/85 backdrop-blur-md p-4 min-w-[208px] shadow-xl">
						<div class="flex items-center justify-between border-b border-white/10 pb-2">
							<span class="font-racing text-xs uppercase tracking-widest text-muted-foreground">Telemetria Box</span>
							<RacingIcon name="speedometer" size="sm" />
						</div>
						<div class="flex items-center justify-between py-0.5">
							<span class="text-xs text-muted-foreground">Ruolo:</span>
							<span class="font-bold text-xs uppercase text-amber-400">
								{auth.isAdmin ? 'Direttore di Gara' : auth.canManageRaces ? 'Giudice di Pista' : 'Pilota Ufficiale'}
							</span>
						</div>
						<div class="flex items-center justify-between py-0.5">
							<span class="text-xs text-muted-foreground">Stato Motore:</span>
							<span class="inline-flex items-center gap-1 font-bold text-xs text-emerald-400">
								<span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
								Pronto
							</span>
						</div>
						<div class="flex items-center justify-between py-0.5">
							<span class="text-xs text-muted-foreground">Meteo:</span>
							<span class="font-medium text-xs text-white">Asfalto Asciutto</span>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Official Game Banner Strip -->
		<div class="relative overflow-hidden rounded-2xl border border-white/10 shadow-xl mb-8 group">
			<img
				src="/images/heat-banner.jpg"
				alt="Heat: Pedal to the Metal — Banner Ufficiale"
				class="w-full h-28 sm:h-36 object-cover object-center transition-transform duration-700 group-hover:scale-105"
			/>
			<div class="absolute inset-0 bg-gradient-to-r from-[#0d1017]/75 via-transparent to-[#0d1017]/60 flex items-center justify-end pr-6 sm:pr-10">
				<div class="text-right">
					<span class="font-racing text-xs uppercase tracking-[0.25em] text-amber-400 font-bold">Days of Wonder</span>
					<p class="font-racing text-white text-sm sm:text-base uppercase tracking-wider font-bold">Il gioco di corse più adrenalinico</p>
				</div>
			</div>
		</div>

		<!-- Action Cards Grid (Garage, Campionati, Negozio) -->
		<div class="grid gap-6 md:grid-cols-3 mb-10">
			<!-- Card 1: Team e Piloti -->
			<a href={resolve('/team')} class="group">
				<div class="relative h-full overflow-hidden rounded-xl border border-white/10 bg-[#141824] p-6 shadow-lg heat-card-hover curb-left flex flex-col justify-between">
					<div class="absolute -right-4 -bottom-4 opacity-5 transition-opacity group-hover:opacity-15">
						<RacingIcon name="helmet" size="2xl" class="scale-150" />
					</div>
					<div>
						<div class="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 border border-primary/20 mb-4 text-primary group-hover:bg-primary group-hover:text-white transition-colors">
							<RacingIcon name="helmet" size="lg" />
						</div>
						<h2 class="font-racing text-2xl font-bold uppercase tracking-wide text-white group-hover:text-heat transition-colors">
							Team e Piloti
						</h2>
						<p class="mt-2 text-xs text-muted-foreground leading-relaxed">
							Crea le tue scuderie, gestisci i piloti iscritti, consulta i mazzi di carte e tieni traccia del bottino in oro accumulato.
						</p>
					</div>
					<div class="mt-6 flex items-center text-xs font-bold uppercase tracking-wider text-primary group-hover:translate-x-1 transition-transform">
						<span>Apri il Garage</span>
						<span class="ml-1">→</span>
					</div>
				</div>
			</a>

			<!-- Card 2: Campionati -->
			<a href={resolve('/championships')} class="group">
				<div class="relative h-full overflow-hidden rounded-xl border border-white/10 bg-[#141824] p-6 shadow-lg heat-card-hover curb-left flex flex-col justify-between">
					<div class="absolute -right-4 -bottom-4 opacity-5 transition-opacity group-hover:opacity-15">
						<RacingIcon name="trophy" size="2xl" class="scale-150" />
					</div>
					<div>
						<div class="flex h-12 w-12 items-center justify-center rounded-lg bg-amber-500/10 border border-amber-500/20 mb-4 text-amber-400 group-hover:bg-amber-500 group-hover:text-white transition-colors">
							<RacingIcon name="trophy" size="lg" />
						</div>
						<h2 class="font-racing text-2xl font-bold uppercase tracking-wide text-white group-hover:text-amber-400 transition-colors">
							Campionati
						</h2>
						<p class="mt-2 text-xs text-muted-foreground leading-relaxed">
							Iscrivi i piloti ai tornei, segui le tappe del circuito, consulta le classifiche a punti e celebra i vincitori sul podio.
						</p>
					</div>
					<div class="mt-6 flex items-center text-xs font-bold uppercase tracking-wider text-amber-400 group-hover:translate-x-1 transition-transform">
						<span>Vai ai Campionati</span>
						<span class="ml-1">→</span>
					</div>
				</div>
			</a>

			<!-- Card 3: Negozio -->
			<a href={resolve('/shop')} class="group">
				<div class="relative h-full overflow-hidden rounded-xl border border-white/10 bg-[#141824] p-6 shadow-lg heat-card-hover curb-left flex flex-col justify-between">
					<div class="absolute -right-4 -bottom-4 opacity-5 transition-opacity group-hover:opacity-15">
						<RacingIcon name="tires" size="2xl" class="scale-150" />
					</div>
					<div>
						<div class="flex h-12 w-12 items-center justify-center rounded-lg bg-sky-500/10 border border-sky-500/20 mb-4 text-sky-400 group-hover:bg-sky-500 group-hover:text-white transition-colors">
							<RacingIcon name="tires" size="lg" />
						</div>
						<h2 class="font-racing text-2xl font-bold uppercase tracking-wide text-white group-hover:text-sky-400 transition-colors">
							Negozio & Officina
						</h2>
						<p class="mt-2 text-xs text-muted-foreground leading-relaxed">
							Spendi l'oro guadagnato in gara per acquistare pacchetti di carte modifica, carte sponsor uniche e potenziare il tuo mazzo.
						</p>
					</div>
					<div class="mt-6 flex items-center text-xs font-bold uppercase tracking-wider text-sky-400 group-hover:translate-x-1 transition-transform">
						<span>Entra nel Negozio</span>
						<span class="ml-1">→</span>
					</div>
				</div>
			</a>
		</div>

		<!-- Board Game Photo Strip -->
		<div class="grid grid-cols-2 gap-4 mb-8">
			<!-- heat-cars photo -->
			<div class="relative overflow-hidden rounded-2xl border border-white/10 shadow-lg group">
				<img
					src="/images/heat-cars.jpg"
					alt="Griglia di partenza — Heat miniature"
					class="w-full h-44 sm:h-56 object-cover object-center transition-transform duration-700 group-hover:scale-105"
				/>
				<div class="absolute inset-0 bg-gradient-to-t from-[#0a0c12]/90 via-[#0a0c12]/30 to-transparent"></div>
				<div class="absolute bottom-3 left-4 right-4">
					<p class="font-racing text-sm sm:text-base uppercase tracking-wider text-white font-bold leading-tight">Griglia di Partenza</p>
					<p class="text-[11px] text-muted-foreground mt-0.5">Le miniature si posizionano per il via</p>
				</div>
			</div>
			<!-- heat-corner photo -->
			<div class="relative overflow-hidden rounded-2xl border border-white/10 shadow-lg group">
				<img
					src="/images/heat-corner.jpg"
					alt="Curva pericolosa — Heat miniature"
					class="w-full h-44 sm:h-56 object-cover object-center transition-transform duration-700 group-hover:scale-105"
				/>
				<div class="absolute inset-0 bg-gradient-to-t from-[#0a0c12]/90 via-[#0a0c12]/30 to-transparent"></div>
				<div class="absolute bottom-3 left-4 right-4">
					<p class="font-racing text-sm sm:text-base uppercase tracking-wider text-white font-bold leading-tight">Curva al Limite</p>
					<p class="text-[11px] text-muted-foreground mt-0.5">Gestisci il calore o finisci nel guard-rail</p>
				</div>
			</div>
		</div>

		<!-- Racing HUD: Board Game Guide & Rules of the Track -->
		<div class="rounded-2xl border border-white/10 bg-[#10141e] p-6 sm:p-8 shadow-xl">
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-4 mb-6">
				<div class="flex items-center gap-3">
					<div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/20 text-primary">
						<RacingIcon name="speedometer" size="md" />
					</div>
					<div>
						<h3 class="font-racing text-2xl font-bold uppercase tracking-wide text-white">
							Manuale del Pilota & Regole di Pista
						</h3>
						<p class="text-xs text-muted-foreground">Strategia di guida e gestione del mazzo Heat</p>
					</div>
				</div>
				<div class="flex items-center gap-2">
					<span class="text-xs font-racing uppercase tracking-wider px-2.5 py-1 rounded bg-white/5 border border-white/10 text-muted-foreground">
						1960s Formula 1 Ruleset
					</span>
				</div>
			</div>

			<div class="grid gap-6 sm:grid-cols-3">
				<!-- Rule 1: Heat Management -->
				<div class="rounded-xl border border-white/5 bg-[#161a26] p-5">
					<div class="flex items-center gap-2 text-primary font-racing text-lg font-bold uppercase tracking-wide mb-2">
						<RacingIcon name="flame" size="sm" />
						<span>1. Gestione del Calore</span>
					</div>
					<p class="text-xs text-muted-foreground leading-relaxed">
						Scalare due marce o accelerare a fondo sposta carte Heat dal motore agli scarti. Quando il motore è vuoto, rischi il testacoda!
					</p>
				</div>

				<!-- Rule 2: Cornering Limits -->
				<div class="rounded-xl border border-white/5 bg-[#161a26] p-5">
					<div class="flex items-center gap-2 text-amber-400 font-racing text-lg font-bold uppercase tracking-wide mb-2">
						<RacingIcon name="speedometer" size="sm" />
						<span>2. Staccate in Curva</span>
					</div>
					<p class="text-xs text-muted-foreground leading-relaxed">
						Ogni curva ha una velocità limite segnalata. Se la oltrepassi, devi pagare una carta Heat per ogni punto di velocità in eccesso.
					</p>
				</div>

				<!-- Rule 3: Slipstream -->
				<div class="rounded-xl border border-white/5 bg-[#161a26] p-5">
					<div class="flex items-center gap-2 text-sky-400 font-racing text-lg font-bold uppercase tracking-wide mb-2">
						<RacingIcon name="car" size="sm" />
						<span>3. Sfrutta la Scia</span>
					</div>
					<p class="text-xs text-muted-foreground leading-relaxed">
						Se finisci il movimento a fianco o subito dietro a un'altra vettura, sfrutta il vortice d'aria per avanzare di 2 caselle bonus gratis!
					</p>
				</div>
			</div>
		</div>
	{/if}
</main>
