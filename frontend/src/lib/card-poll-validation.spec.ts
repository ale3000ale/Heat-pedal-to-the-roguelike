import { describe, expect, it } from 'vitest';
import { CARD_POLL_DEFAULT, parseCardPoll } from './card-poll-validation';

describe('parseCardPoll', () => {
	it('accetta i valori da 1 a 10', () => {
		expect(parseCardPoll('1')).toEqual({ seconds: 1 });
		expect(parseCardPoll('5')).toEqual({ seconds: 5 });
		expect(parseCardPoll(' 10 ')).toEqual({ seconds: 10 });
	});

	it('rifiuta i valori fuori dai limiti', () => {
		expect(parseCardPoll('0')).toHaveProperty('error');
		expect(parseCardPoll('11')).toHaveProperty('error');
	});

	it('rifiuta testo, decimali, negativi e campo vuoto', () => {
		for (const text of ['', 'abc', '2.5', '-3', '1e1']) {
			expect(parseCardPoll(text)).toHaveProperty('error');
		}
	});

	it('il predefinito è 5 e rientra nei limiti', () => {
		expect(parseCardPoll(String(CARD_POLL_DEFAULT))).toEqual({ seconds: 5 });
	});
});
