<script lang="ts">
	let {
		name,
		size = 'md',
		class: className = '',
		color = 'currentColor'
	}: {
		name:
			| 'flags'
			| 'trophy'
			| 'helmet'
			| 'speedometer'
			| 'pistons'
			| 'wrenches'
			| 'stopwatch'
			| 'tires'
			| 'spark_plug'
			| 'laurel'
			| 'flame'
			| 'car'
			| 'gear';
		size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | number;
		class?: string;
		color?: string;
	} = $props();

	const sizeMap: Record<string, string> = {
		xs: 'w-3.5 h-3.5',
		sm: 'w-4 h-4',
		md: 'w-5 h-5',
		lg: 'w-6 h-6',
		xl: 'w-8 h-8',
		'2xl': 'w-12 h-12'
	};

	let sizeClass = $derived(typeof size === 'number' ? '' : sizeMap[size] || 'w-5 h-5');
	let inlineStyle = $derived(typeof size === 'number' ? `width: ${size}px; height: ${size}px;` : '');
</script>

{#if name === 'flags'}
	<!-- Crossed Checkered Flags -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Left flag pole -->
		<line x1="8" y1="56" x2="52" y2="12" stroke={color} stroke-width="3" stroke-linecap="round" />
		<circle cx="53" cy="11" r="2.5" fill="#f59e0b" />
		<!-- Right flag pole -->
		<line x1="56" y1="56" x2="12" y2="12" stroke={color} stroke-width="3" stroke-linecap="round" />
		<circle cx="11" cy="11" r="2.5" fill="#f59e0b" />

		<!-- Left flag fabric -->
		<path
			d="M14 14 C 22 10, 26 22, 34 18 L 30 36 C 22 40, 18 28, 10 32 Z"
			fill="#ffffff"
			stroke={color}
			stroke-width="1.5"
		/>
		<path d="M14 14 C 18 12, 20 18, 24 16 L 23 25 C 19 27, 17 21, 12 23 Z" fill="#111827" />
		<path d="M24 16 C 28 14, 30 20, 34 18 L 32 27 C 28 29, 26 23, 22 25 Z" fill="#e63926" />
		<path d="M12 23 C 16 21, 18 27, 22 25 L 21 34 C 17 36, 15 30, 10 32 Z" fill="#111827" />
		<path d="M22 25 C 26 23, 28 29, 32 27 L 30 36 C 26 38, 24 32, 20 34 Z" fill="#ffffff" />

		<!-- Right flag fabric -->
		<path
			d="M50 14 C 42 10, 38 22, 30 18 L 34 36 C 42 40, 46 28, 54 32 Z"
			fill="#ffffff"
			stroke={color}
			stroke-width="1.5"
		/>
		<path d="M50 14 C 46 12, 44 18, 40 16 L 41 25 C 45 27, 47 21, 52 23 Z" fill="#111827" />
		<path d="M40 16 C 36 14, 34 20, 30 18 L 32 27 C 36 29, 38 23, 42 25 Z" fill="#e63926" />
		<path d="M52 23 C 48 21, 46 27, 42 25 L 43 34 C 47 36, 49 30, 54 32 Z" fill="#111827" />
		<path d="M42 25 C 38 23, 36 29, 32 27 L 34 36 C 38 38, 40 32, 44 34 Z" fill="#ffffff" />
	</svg>
{:else if name === 'trophy'}
	<!-- Grand Prix Trophy Cup -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Left handle -->
		<path
			d="M20 18 C 8 18, 8 34, 22 36"
			stroke="#f59e0b"
			stroke-width="3"
			stroke-linecap="round"
			fill="none"
		/>
		<!-- Right handle -->
		<path
			d="M44 18 C 56 18, 56 34, 42 36"
			stroke="#f59e0b"
			stroke-width="3"
			stroke-linecap="round"
			fill="none"
		/>
		<!-- Cup Body -->
		<path
			d="M18 12 L 46 12 C 46 28, 40 40, 32 42 C 24 40, 18 28, 18 12 Z"
			fill="url(#trophy-grad)"
			stroke="#d97706"
			stroke-width="2"
		/>
		<!-- Cup Rim -->
		<rect x="16" y="10" width="32" height="4" rx="2" fill="#fbbf24" stroke="#d97706" stroke-width="1.5" />
		<!-- Star badge on cup -->
		<path
			d="M32 22 L 33.5 26.5 L 38 26.5 L 34.5 29 L 36 33.5 L 32 30.5 L 28 33.5 L 29.5 29 L 26 26.5 L 30.5 26.5 Z"
			fill="#ffffff"
		/>
		<!-- Stem -->
		<path d="M30 42 L 34 42 L 35 50 L 29 50 Z" fill="#d97706" />
		<!-- Base block -->
		<path d="M22 50 L 42 50 L 45 56 L 19 56 Z" fill="#1f2937" stroke="#d97706" stroke-width="1.5" />
		<rect x="25" y="52" width="14" height="2" rx="0.5" fill="#f59e0b" />
		<defs>
			<linearGradient id="trophy-grad" x1="18" y1="12" x2="46" y2="42" gradientUnits="userSpaceOnUse">
				<stop offset="0%" stop-color="#fef08a" />
				<stop offset="50%" stop-color="#f59e0b" />
				<stop offset="100%" stop-color="#b45309" />
			</linearGradient>
		</defs>
	</svg>
{:else if name === 'helmet'}
	<!-- Vintage Racing Helmet -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Helmet shell -->
		<path
			d="M12 36 C 12 18, 22 10, 40 10 C 52 10, 56 20, 56 34 C 56 46, 48 52, 38 52 C 26 52, 20 48, 14 48 C 12 48, 12 42, 12 36 Z"
			fill="url(#helmet-grad)"
			stroke="#991b1b"
			stroke-width="2"
		/>
		<!-- Racing stripe -->
		<path
			d="M26 11 C 32 10.5, 36 10.5, 42 11 L 40 18 C 36 17.5, 32 17.5, 28 18 Z"
			fill="#ffffff"
		/>
		<!-- Goggles / Visor cutout -->
		<path
			d="M34 24 C 44 24, 52 28, 54 34 C 54 38, 46 40, 36 40 C 32 40, 30 36, 30 32 C 30 27, 31 24, 34 24 Z"
			fill="#111827"
			stroke="#374151"
			stroke-width="1.5"
		/>
		<!-- Visor glass reflection -->
		<path d="M36 27 C 42 27, 48 30, 50 33 L 46 36 C 43 33, 38 31, 35 32 Z" fill="#60a5fa" opacity="0.8" />
		<!-- Chin vent -->
		<rect x="22" y="44" width="8" height="2" rx="1" fill="#111827" />
		<!-- Side rivet -->
		<circle cx="28" cy="34" r="2.5" fill="#d1d5db" stroke="#374151" stroke-width="1" />
		<defs>
			<linearGradient id="helmet-grad" x1="12" y1="10" x2="56" y2="52" gradientUnits="userSpaceOnUse">
				<stop offset="0%" stop-color="#ef4444" />
				<stop offset="60%" stop-color="#dc2626" />
				<stop offset="100%" stop-color="#991b1b" />
			</linearGradient>
		</defs>
	</svg>
{:else if name === 'speedometer'}
	<!-- Dashboard Speedometer / Tachometer Gauge -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Outer dial ring -->
		<circle cx="32" cy="32" r="28" fill="#111827" stroke="#374151" stroke-width="2.5" />
		<!-- Inner bezel -->
		<circle cx="32" cy="32" r="24" stroke="#4b5563" stroke-width="1" fill="#0f172a" />
		<!-- Redline danger zone arc -->
		<path
			d="M 44 15 A 22 22 0 0 1 54 32"
			stroke="#ef4444"
			stroke-width="3"
			stroke-linecap="round"
			fill="none"
		/>
		<!-- Gauge tick marks -->
		<line x1="14" y1="32" x2="18" y2="32" stroke="#9ca3af" stroke-width="2" />
		<line x1="17" y1="21" x2="21" y2="23" stroke="#9ca3af" stroke-width="2" />
		<line x1="24" y1="14" x2="26" y2="18" stroke="#9ca3af" stroke-width="2" />
		<line x1="32" y1="11" x2="32" y2="16" stroke="#9ca3af" stroke-width="2" />
		<line x1="40" y1="14" x2="38" y2="18" stroke="#f59e0b" stroke-width="2" />
		<line x1="47" y1="21" x2="43" y2="23" stroke="#ef4444" stroke-width="2" />
		<line x1="50" y1="32" x2="46" y2="32" stroke="#ef4444" stroke-width="2" />
		<!-- Needle pointing high RPM -->
		<line x1="32" y1="32" x2="44" y2="18" stroke="#e63926" stroke-width="2.5" stroke-linecap="round" />
		<!-- Center hub -->
		<circle cx="32" cy="32" r="4.5" fill="#f59e0b" stroke="#111827" stroke-width="1.5" />
		<!-- Small digital / odometer readout -->
		<rect x="25" y="40" width="14" height="6" rx="1.5" fill="#1e293b" stroke="#334155" stroke-width="1" />
		<text x="32" y="44.5" font-size="4" font-family="monospace" fill="#38bdf8" text-anchor="middle" font-weight="bold">RPM</text>
	</svg>
{:else if name === 'pistons'}
	<!-- Crossed Engine Pistons -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Left piston rod & head -->
		<g transform="rotate(-35 32 32)">
			<rect x="26" y="8" width="12" height="18" rx="2" fill="#cbd5e1" stroke="#334155" stroke-width="1.5" />
			<line x1="26" y1="13" x2="38" y2="13" stroke="#475569" stroke-width="1" />
			<line x1="26" y1="17" x2="38" y2="17" stroke="#475569" stroke-width="1" />
			<!-- Connecting rod -->
			<rect x="29" y="26" width="6" height="26" fill="#94a3b8" stroke="#334155" stroke-width="1" />
			<circle cx="32" cy="50" r="5" fill="#64748b" stroke="#334155" stroke-width="1.5" />
			<circle cx="32" cy="50" r="2" fill="#0f172a" />
		</g>
		<!-- Right piston rod & head -->
		<g transform="rotate(35 32 32)">
			<rect x="26" y="8" width="12" height="18" rx="2" fill="#cbd5e1" stroke="#334155" stroke-width="1.5" />
			<line x1="26" y1="13" x2="38" y2="13" stroke="#475569" stroke-width="1" />
			<line x1="26" y1="17" x2="38" y2="17" stroke="#475569" stroke-width="1" />
			<!-- Connecting rod -->
			<rect x="29" y="26" width="6" height="26" fill="#94a3b8" stroke="#334155" stroke-width="1" />
			<circle cx="32" cy="50" r="5" fill="#64748b" stroke="#334155" stroke-width="1.5" />
			<circle cx="32" cy="50" r="2" fill="#0f172a" />
		</g>
	</svg>
{:else if name === 'wrenches'}
	<!-- Crossed Spanners / Wrenches -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<g transform="rotate(45 32 32)">
			<rect x="29" y="14" width="6" height="36" rx="2" fill="#94a3b8" stroke="#334155" stroke-width="1.5" />
			<!-- Top jaw -->
			<path d="M26 14 C 26 8, 38 8, 38 14 C 36 17, 34 17, 32 15 C 30 17, 28 17, 26 14 Z" fill="#cbd5e1" stroke="#334155" stroke-width="1.5" />
			<!-- Bottom ring -->
			<circle cx="32" cy="50" r="5" fill="#cbd5e1" stroke="#334155" stroke-width="1.5" />
			<circle cx="32" cy="50" r="2.5" fill="#0f172a" />
		</g>
		<g transform="rotate(-45 32 32)">
			<rect x="29" y="14" width="6" height="36" rx="2" fill="#94a3b8" stroke="#334155" stroke-width="1.5" />
			<path d="M26 14 C 26 8, 38 8, 38 14 C 36 17, 34 17, 32 15 C 30 17, 28 17, 26 14 Z" fill="#cbd5e1" stroke="#334155" stroke-width="1.5" />
			<circle cx="32" cy="50" r="5" fill="#cbd5e1" stroke="#334155" stroke-width="1.5" />
			<circle cx="32" cy="50" r="2.5" fill="#0f172a" />
		</g>
	</svg>
{:else if name === 'stopwatch'}
	<!-- Vintage Chronometer -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Top button / crown -->
		<rect x="29" y="6" width="6" height="6" rx="1.5" fill="#94a3b8" stroke="#334155" stroke-width="1.5" />
		<path d="M26 4 L 38 4" stroke="#64748b" stroke-width="2.5" stroke-linecap="round" />
		<!-- Side lap button -->
		<path d="M46 14 L 50 10" stroke="#64748b" stroke-width="3" stroke-linecap="round" />
		<!-- Watch body -->
		<circle cx="32" cy="36" r="22" fill="#1e293b" stroke="#cbd5e1" stroke-width="3" />
		<circle cx="32" cy="36" r="18" fill="#0f172a" stroke="#475569" stroke-width="1" />
		<!-- Ticks -->
		<line x1="32" y1="20" x2="32" y2="23" stroke="#ef4444" stroke-width="2" />
		<line x1="48" y1="36" x2="45" y2="36" stroke="#94a3b8" stroke-width="1.5" />
		<line x1="32" y1="52" x2="32" y2="49" stroke="#94a3b8" stroke-width="1.5" />
		<line x1="16" y1="36" x2="19" y2="36" stroke="#94a3b8" stroke-width="1.5" />
		<!-- Chrono hand -->
		<line x1="32" y1="36" x2="39" y2="24" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" />
		<circle cx="32" cy="36" r="3" fill="#ef4444" />
	</svg>
{:else if name === 'tires'}
	<!-- Racing Tires -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Tire 1 -->
		<rect x="8" y="14" width="14" height="36" rx="5" fill="#1e293b" stroke="#475569" stroke-width="2" />
		<line x1="11" y1="20" x2="19" y2="20" stroke="#334155" stroke-width="2" />
		<line x1="11" y1="28" x2="19" y2="28" stroke="#334155" stroke-width="2" />
		<line x1="11" y1="36" x2="19" y2="36" stroke="#334155" stroke-width="2" />
		<line x1="11" y1="44" x2="19" y2="44" stroke="#334155" stroke-width="2" />
		<!-- Tire 2 (center, bigger) -->
		<rect x="25" y="10" width="14" height="44" rx="5" fill="#0f172a" stroke="#e63926" stroke-width="2" />
		<line x1="28" y1="18" x2="36" y2="18" stroke="#e63926" stroke-width="2" />
		<line x1="28" y1="26" x2="36" y2="26" stroke="#e63926" stroke-width="2" />
		<line x1="28" y1="34" x2="36" y2="34" stroke="#e63926" stroke-width="2" />
		<line x1="28" y1="42" x2="36" y2="42" stroke="#e63926" stroke-width="2" />
		<line x1="28" y1="48" x2="36" y2="48" stroke="#e63926" stroke-width="2" />
		<!-- Tire 3 -->
		<rect x="42" y="14" width="14" height="36" rx="5" fill="#1e293b" stroke="#475569" stroke-width="2" />
		<line x1="45" y1="20" x2="53" y2="20" stroke="#334155" stroke-width="2" />
		<line x1="45" y1="28" x2="53" y2="28" stroke="#334155" stroke-width="2" />
		<line x1="45" y1="36" x2="53" y2="36" stroke="#334155" stroke-width="2" />
		<line x1="45" y1="44" x2="53" y2="44" stroke="#334155" stroke-width="2" />
	</svg>
{:else if name === 'spark_plug'}
	<!-- Spark Plug -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Terminal -->
		<rect x="29" y="6" width="6" height="6" rx="1.5" fill="#94a3b8" />
		<!-- Ceramic insulator ribs -->
		<rect x="28" y="12" width="8" height="3" fill="#ffffff" stroke="#64748b" stroke-width="0.8" />
		<rect x="27" y="15" width="10" height="3" fill="#ffffff" stroke="#64748b" stroke-width="0.8" />
		<rect x="28" y="18" width="8" height="3" fill="#ffffff" stroke="#64748b" stroke-width="0.8" />
		<rect x="27" y="21" width="10" height="4" fill="#ffffff" stroke="#64748b" stroke-width="0.8" />
		<!-- Hex nut -->
		<path d="M24 25 L 40 25 L 38 33 L 26 33 Z" fill="#64748b" stroke="#334155" stroke-width="1.5" />
		<!-- Threaded body -->
		<rect x="27" y="33" width="10" height="16" fill="#475569" stroke="#334155" stroke-width="1" />
		<line x1="27" y1="37" x2="37" y2="37" stroke="#94a3b8" stroke-width="1.2" />
		<line x1="27" y1="41" x2="37" y2="41" stroke="#94a3b8" stroke-width="1.2" />
		<line x1="27" y1="45" x2="37" y2="45" stroke="#94a3b8" stroke-width="1.2" />
		<!-- Electrode & Spark -->
		<rect x="30" y="49" width="4" height="6" fill="#cbd5e1" />
		<path d="M27 57 L 33 57 L 33 55" stroke="#94a3b8" stroke-width="2" fill="none" />
		<!-- Electric Spark -->
		<path d="M31 54 L 33 52 L 32 55 L 35 53" stroke="#38bdf8" stroke-width="1.5" stroke-linecap="round" />
	</svg>
{:else if name === 'laurel'}
	<!-- Grand Prix Victory Laurel Wreath -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Left wreath branch -->
		<path
			d="M20 50 C 10 40, 10 20, 24 12"
			stroke="#f59e0b"
			stroke-width="2"
			stroke-linecap="round"
			fill="none"
		/>
		<!-- Left leaves -->
		<ellipse cx="14" cy="42" rx="3.5" ry="2" transform="rotate(-30 14 42)" fill="#fbbf24" />
		<ellipse cx="11" cy="33" rx="3.5" ry="2" transform="rotate(-10 11 33)" fill="#fbbf24" />
		<ellipse cx="13" cy="24" rx="3.5" ry="2" transform="rotate(20 13 24)" fill="#fbbf24" />
		<ellipse cx="18" cy="16" rx="3.5" ry="2" transform="rotate(45 18 16)" fill="#fbbf24" />
		<ellipse cx="24" cy="12" rx="3" ry="1.8" transform="rotate(60 24 12)" fill="#fbbf24" />

		<!-- Right wreath branch -->
		<path
			d="M44 50 C 54 40, 54 20, 40 12"
			stroke="#f59e0b"
			stroke-width="2"
			stroke-linecap="round"
			fill="none"
		/>
		<!-- Right leaves -->
		<ellipse cx="50" cy="42" rx="3.5" ry="2" transform="rotate(30 50 42)" fill="#fbbf24" />
		<ellipse cx="53" cy="33" rx="3.5" ry="2" transform="rotate(10 53 33)" fill="#fbbf24" />
		<ellipse cx="51" cy="24" rx="3.5" ry="2" transform="rotate(-20 51 24)" fill="#fbbf24" />
		<ellipse cx="46" cy="16" rx="3.5" ry="2" transform="rotate(-45 46 16)" fill="#fbbf24" />
		<ellipse cx="40" cy="12" rx="3" ry="1.8" transform="rotate(-60 40 12)" fill="#fbbf24" />

		<!-- Ribbon tie at bottom -->
		<path d="M26 50 C 32 53, 38 53, 44 50 L 41 57 L 35 53 L 29 57 Z" fill="#e63926" stroke="#991b1b" stroke-width="1" />
		<!-- Center Star -->
		<circle cx="32" cy="30" r="3" fill="#f59e0b" />
	</svg>
{:else if name === 'flame'}
	<!-- Heat Engine Roaring Fire Flame -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Outer flame -->
		<path
			d="M32 8 C 36 20, 48 24, 48 38 C 48 49, 41 56, 32 56 C 23 56, 16 49, 16 38 C 16 26, 26 22, 28 14 C 28 14, 25 24, 32 8 Z"
			fill="url(#outer-flame)"
		/>
		<!-- Middle flame -->
		<path
			d="M32 20 C 35 28, 42 32, 42 42 C 42 48, 38 52, 32 52 C 26 52, 22 48, 22 42 C 22 34, 28 30, 30 24 Z"
			fill="url(#mid-flame)"
		/>
		<!-- Inner core flame -->
		<path
			d="M32 34 C 34 38, 37 40, 37 45 C 37 48, 35 50, 32 50 C 29 50, 27 48, 27 45 C 27 40, 31 38, 32 34 Z"
			fill="#ffffff"
		/>
		<defs>
			<linearGradient id="outer-flame" x1="32" y1="8" x2="32" y2="56" gradientUnits="userSpaceOnUse">
				<stop offset="0%" stop-color="#ff7a00" />
				<stop offset="60%" stop-color="#e63926" />
				<stop offset="100%" stop-color="#b91c1c" />
			</linearGradient>
			<linearGradient id="mid-flame" x1="32" y1="20" x2="32" y2="52" gradientUnits="userSpaceOnUse">
				<stop offset="0%" stop-color="#fef08a" />
				<stop offset="60%" stop-color="#f59e0b" />
				<stop offset="100%" stop-color="#e63926" />
			</linearGradient>
		</defs>
	</svg>
{:else if name === 'car'}
	<!-- Vintage Formula 1 Cigar Car Silhouette -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Rear Wheels -->
		<rect x="6" y="16" width="8" height="14" rx="3" fill="#0f172a" stroke="#334155" stroke-width="1.5" />
		<rect x="6" y="34" width="8" height="14" rx="3" fill="#0f172a" stroke="#334155" stroke-width="1.5" />
		<!-- Front Wheels -->
		<rect x="50" y="18" width="7" height="11" rx="2.5" fill="#0f172a" stroke="#334155" stroke-width="1.5" />
		<rect x="50" y="35" width="7" height="11" rx="2.5" fill="#0f172a" stroke="#334155" stroke-width="1.5" />
		<!-- Suspension arms -->
		<line x1="14" y1="23" x2="20" y2="28" stroke="#64748b" stroke-width="2" />
		<line x1="14" y1="41" x2="20" y2="36" stroke="#64748b" stroke-width="2" />
		<line x1="48" y1="24" x2="42" y2="28" stroke="#64748b" stroke-width="2" />
		<line x1="48" y1="40" x2="42" y2="36" stroke="#64748b" stroke-width="2" />
		<!-- Cigar body -->
		<path
			d="M12 28 C 16 26, 32 26, 56 31 C 58 32, 58 32, 56 33 C 32 38, 16 38, 12 36 Z"
			fill="url(#car-body-grad)"
			stroke="#991b1b"
			stroke-width="1.5"
		/>
		<!-- Cockpit opening -->
		<ellipse cx="28" cy="32" rx="4" ry="2.5" fill="#0f172a" />
		<!-- Driver Helmet -->
		<circle cx="27" cy="32" r="3" fill="#ffffff" stroke="#e63926" stroke-width="1" />
		<!-- Racing number oval -->
		<circle cx="42" cy="32" r="3" fill="#ffffff" stroke="#111827" stroke-width="0.8" />
		<!-- Exhaust flame spitting from back -->
		<path d="M10 32 L 3 30 L 5 32 L 2 34 Z" fill="#f59e0b" />
		<defs>
			<linearGradient id="car-body-grad" x1="12" y1="28" x2="56" y2="36" gradientUnits="userSpaceOnUse">
				<stop offset="0%" stop-color="#b91c1c" />
				<stop offset="50%" stop-color="#e63926" />
				<stop offset="100%" stop-color="#ff7a00" />
			</linearGradient>
		</defs>
	</svg>
{:else if name === 'gear'}
	<!-- 4-Speed Gear Shifter -->
	<svg
		viewBox="0 0 64 64"
		fill="none"
		xmlns="http://www.w3.org/2000/svg"
		class="{sizeClass} {className} shrink-0 inline-block align-middle"
		style={inlineStyle}
		aria-hidden="true"
	>
		<!-- Chrome shift gate -->
		<rect x="14" y="14" width="36" height="36" rx="8" fill="#1e293b" stroke="#cbd5e1" stroke-width="2.5" />
		<!-- H-pattern track -->
		<path
			d="M24 22 L 24 42 M 40 22 L 40 42 M 24 32 L 40 32"
			stroke="#f8fafc"
			stroke-width="3"
			stroke-linecap="round"
		/>
		<!-- Gear numbers -->
		<text x="24" y="20" font-size="5" font-family="sans-serif" font-weight="bold" fill="#f59e0b" text-anchor="middle">1</text>
		<text x="40" y="20" font-size="5" font-family="sans-serif" font-weight="bold" fill="#f59e0b" text-anchor="middle">3</text>
		<text x="24" y="47" font-size="5" font-family="sans-serif" font-weight="bold" fill="#f59e0b" text-anchor="middle">2</text>
		<text x="40" y="47" font-size="5" font-family="sans-serif" font-weight="bold" fill="#e63926" text-anchor="middle">4</text>
		<!-- Shift knob in 3rd gear -->
		<circle cx="40" cy="22" r="5" fill="#e63926" stroke="#ffffff" stroke-width="1.5" />
	</svg>
{/if}
