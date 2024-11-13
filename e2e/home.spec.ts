import { expect, test } from '@playwright/test';

test('エレベーターが1階にいる時、階の表示が1になっている', async ({ page }) => {
	await page.goto('http://localhost:3000');

	await expect(page.getByRole('main')).toHaveText(/1F/);
});

test('人が2階でボタンを押すと、階の表示が2になっている', async ({ page }) => {
	await page.goto('http://localhost:3000');
  await page.getByRole('button', { name: '下' }).click();

	await expect(page.getByRole('main')).toHaveText(/2F/);
});
