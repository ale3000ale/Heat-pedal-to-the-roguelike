import { describe, expect, it } from 'vitest';
import { boardPoolImageUrl } from './board-pool-api';

describe('pool di mappe ed eventi', () => {
	it('costruisce l URL servito da media', () => {
		expect(boardPoolImageUrl('board/maps/DEUTSCHLAND.webp')).toBe(
			'/media/board/maps/DEUTSCHLAND.webp'
		);
		expect(boardPoolImageUrl('board\\events\\AFFLUENZA RECORD.webp')).toBe(
			'/media/board/events/AFFLUENZA RECORD.webp'
		);
	});
});
