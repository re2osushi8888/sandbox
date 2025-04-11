'use client';
import { useState } from 'react';

export default function Home() {
	const [floor, setFloor] = useState('1F');
	const changeTo2F = () => {
		setFloor('2F');
	};
	const changeTo1F = () => {
		setFloor('1F');
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
			<button type={'button'} onClick={changeTo1F}>
				上
			</button>
		</main>
	);
}
