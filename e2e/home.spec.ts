import { expect, test } from '@playwright/test';

test('ページ表示のテスト', async ({ page }) => {
	await page.goto('http://localhost:3000');
	await expect(page).toHaveTitle(/最初のページ/);
	await expect(page.getByRole('heading')).toHaveText(/Playwrightのハンズオン/);
	await expect(page.getByRole('button', { name: /操作ボタン/ })).toBeVisible();
});
