import { describe, expect, it } from 'vitest';
import { raceStatusView } from './race-status';

describe('raceStatusView', () => {
	it('mostra "in corso" in rosso', () => {
		expect(raceStatusView('in_progress')).toEqual({ label: 'in corso', class: 'text-red-600' });
	});

	it('mostra "in revisione" in ambra durante la revisione', () => {
		expect(raceStatusView('in_review')).toEqual({
			label: 'in revisione',
			class: 'text-amber-600'
		});
	});

	it('mostra "da rivedere" come "in revisione"', () => {
		expect(raceStatusView('to_review')).toEqual(raceStatusView('in_review'));
	});

	it('mostra "terminata" in verde', () => {
		expect(raceStatusView('closed')).toEqual({ label: 'terminata', class: 'text-green-600' });
	});
});
