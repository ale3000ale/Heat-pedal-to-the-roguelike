import { describe, expect, it } from 'vitest';
import { createRawSnippet } from 'svelte';
import { render } from 'svelte/server';
import NavDrawer from './nav-drawer.svelte';
import NavMenu from './nav-menu.svelte';

// Solo SSR: non verifica clic, Escape, focus o comportamento responsive reale.
function content() {
	return createRawSnippet(() => ({
		render: () => '<ul><li>Voce di prova</li></ul>'
	}));
}

describe('drawer di navigazione', () => {
	it('non renderizza nulla da chiuso', () => {
		const body = render(NavDrawer, { props: { open: false, children: content() } }).body;
		expect(body).not.toContain('role="dialog"');
		expect(body).not.toContain('id="nav-drawer"');
	});

	it('renderizza il pannello laterale da aperto', () => {
		const body = render(NavDrawer, { props: { open: true, children: content() } }).body;
		expect(body).toContain('id="nav-drawer"');
		expect(body).toContain('role="dialog"');
		expect(body).toContain('aria-modal="true"');
		expect(body).toContain('aria-label="Navigazione"');
		expect(body).toContain('Voce di prova');
	});
});

describe('voci di navigazione', () => {
	it('mostra le tre voci principali e segna quella attiva', () => {
		const body = render(NavMenu, { props: { currentPath: '/shop', isAdmin: false } }).body;
		expect(body).toContain('href="/team"');
		expect(body).toContain('href="/championships"');
		expect(body).toContain('href="/shop"');
		expect(body).toContain('aria-current="page"');
		expect(body).not.toContain('href="/admin/pools"');
	});

	it('aggiunge le voci admin solo per un admin', () => {
		const senza = render(NavMenu, { props: { currentPath: '/', isAdmin: false } }).body;
		const con = render(NavMenu, { props: { currentPath: '/', isAdmin: true } }).body;
		expect(senza).not.toContain('href="/admin/users"');
		expect(con).toContain('href="/admin/championships"');
		expect(con).toContain('href="/admin/pools"');
		expect(con).toContain('href="/admin/shop"');
		expect(con).toContain('href="/admin/users"');
	});

	it('in verticale mostra le voci admin senza menu a tendina', () => {
		const orizzontale = render(NavMenu, {
			props: { currentPath: '/admin/pools', isAdmin: true }
		}).body;
		const verticale = render(NavMenu, {
			props: { currentPath: '/admin/pools', isAdmin: true, orientation: 'vertical' }
		}).body;
		expect(orizzontale).toContain('<details');
		expect(verticale).not.toContain('<details');
		expect(verticale).toContain('Admin');
		expect(verticale).toContain('href="/admin/users"');
	});
});
