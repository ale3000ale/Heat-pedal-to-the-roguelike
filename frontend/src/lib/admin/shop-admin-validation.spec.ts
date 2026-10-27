import { describe, expect, it } from 'vitest';
import {
	emptyPackForm,
	formFromPack,
	toPackData,
	validatePackForm,
	validateShopTemplate
} from './shop-admin-validation';

describe('validatePackForm', () => {
	it('accetta il modulo di partenza con un nome', () => {
		expect(validatePackForm({ ...emptyPackForm(), name: 'Base' })).toBeNull();
	});

	it('rifiuta il nome vuoto', () => {
		expect(validatePackForm(emptyPackForm())).not.toBeNull();
	});

	it('rifiuta un costo non positivo', () => {
		const form = { ...emptyPackForm(), name: 'Base', cost: 0 };
		expect(validatePackForm(form)).not.toBeNull();
	});

	it('rifiuta un pacchetto senza carte', () => {
		const form = { ...emptyPackForm(), name: 'Vuoto', modifiche_count: 0, sponsor_count: 0 };
		expect(validatePackForm(form)).not.toBeNull();
	});

	it('richiede almeno un nome nel filtro attivo', () => {
		const form = { ...emptyPackForm(), name: 'F', filter_enabled: true, filter_text: ' , ' };
		expect(validatePackForm(form)).not.toBeNull();
	});
});

describe('toPackData', () => {
	it('converte immagine e filtro vuoti in null', () => {
		const data = toPackData({ ...emptyPackForm(), name: ' Base ' });
		expect(data.name).toBe('Base');
		expect(data.image_path).toBeNull();
		expect(data.filter_text).toBeNull();
	});
});

describe('formFromPack', () => {
	it('copia i campi di un template', () => {
		const form = formFromPack({
			name: 'Turbo',
			image_path: 'illustration/turbo.webp',
			currency: 'sponsor',
			cost: 5,
			modifiche_count: 1,
			sponsor_count: 2,
			filter_enabled: false,
			filter_text: null
		});
		expect(form.currency).toBe('sponsor');
		expect(form.filter_text).toBe('');
	});
});

describe('validateShopTemplate', () => {
	it('richiede almeno un pacchetto solo in creazione', () => {
		expect(validateShopTemplate('Negozio', [], true)).not.toBeNull();
		expect(validateShopTemplate('Negozio', [], false)).toBeNull();
	});

	it('rifiuta un nome troppo corto', () => {
		expect(validateShopTemplate('A', [1], true)).not.toBeNull();
	});
});
