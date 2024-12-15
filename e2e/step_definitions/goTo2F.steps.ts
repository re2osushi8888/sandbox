import { Before, Given, Then, When } from '@cucumber/cucumber';
import { type Page, chromium, expect } from '@playwright/test';

let page: Page;

Before(async () => {
	const browser = await chromium.launch({ headless: false }); // headless: true にするとブラウザが表示されない
	const context = await browser.newContext();
	page = await context.newPage();
});
Given('かごが1階にある', async () => {
	await page.goto('http://localhost:3000');
});

When('"下"ボタンを押す', async () => {
	await page.getByRole('button', { name: '下' }).click();
});

Then('"2F"と表示される', async () => {
	await expect(page.getByRole('main')).toHaveText(/2F/);
});
