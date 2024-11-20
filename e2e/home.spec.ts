import { type Page, expect, test } from '@playwright/test';

async function かごが2Fに移動する(page: Page) {
	await page.getByRole('button', { name: '下' }).click();
}

test.describe('かごが1階にいる時', () => {
	test('階の表示が1になっている', async ({
		page,
	}) => {
		await page.goto('http://localhost:3000');

		await expect(page.getByRole('main')).toHaveText(/1F/);
	});

	test('人が2階で下ボタンを押すと、階の表示が2になっている', async ({
		page,
	}) => {
		await page.goto('http://localhost:3000');
		await page.getByRole('button', { name: '下' }).click();

		await expect(page.getByRole('main')).toHaveText(/2F/);
	});
});

test.describe('かごが2階にいる時', () => {
	test('人が1階で上ボタンを押すと、階の表示が1になっている', async ({
		page,
	}) => {
		await page.goto('http://localhost:3000');
		await かごが2Fに移動する(page);
		await page.getByRole('button', { name: '上' }).click();

		await expect(page.getByRole('main')).toHaveText(/1F/);
	});
});
