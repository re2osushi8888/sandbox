import { Before, Given, Then, When } from '@cucumber/cucumber';
import { type Page, chromium, expect } from '@playwright/test';

let page: Page;

Before(async () => {
	const browser = await chromium.launch({ headless: false }); // headless: true にするとブラウザが表示されない
	const context = await browser.newContext();
	page = await context.newPage();
});
Given('最初のページにアクセスする', async () => {
	await page.goto('http://localhost:3000');
});
Then('階の表示が"1F"になっている', async () => {
	await expect(page.getByRole('main')).toHaveText(/1F/);
});


When('"下"ボタンを押す', async () => {
	await page.getByRole('button', { name: '下' }).click();
});
Then('階の表示が"2F"と表示される', async () => {
	await expect(page.getByRole('main')).toHaveText(/2F/);
});
