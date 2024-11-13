import type { Metadata } from 'next';

export const metadata: Metadata = {
	title: '最初のページ',
	description: 'Playwrightハンズオンの最初のステップ'
};

export default function Home() {
	return (
		<main>
			<h1>Playwrightのハンズオン</h1>
			<p>あなたは1習慣後にはE2Eテストのエキスパートです。</p>
			<p>
				<button type="button">操作ボタン</button>
			</p>
		</main>
	);
}
