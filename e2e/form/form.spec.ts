import { test } from '@playwright/test';

test('test', async ({ page }) => {
	await page.goto('http://localhost:3000/');
	await page.getByRole('link', { name: '入力フォーム' }).click();
	await page.getByRole('heading', { name: '入力フォーム' }).click();
});
