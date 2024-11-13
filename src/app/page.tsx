import type { Metadata } from 'next';

export const metadata: Metadata = {
	title: '最初のページ',
	description: 'Playwrightハンズオンの最初のステップ',
};

export default function Home() {
	return (
		<main>
			<div>
				現在の階:
				<span>1F</span>
			</div>
		</main>
	);
}
