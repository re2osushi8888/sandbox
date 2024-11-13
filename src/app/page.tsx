'use client';
import { useState } from 'react';

export default function Home() {
	const [floor, setFloor] = useState('1F');
	const changeTo2F = () => {
		setFloor('2F');
	};

	return (
		<main>
			<div>
				現在の階:
				<span>{floor}</span>
			</div>
			<button type={'button'} onClick={changeTo2F}>
				下
			</button>
		</main>
	);
}
