import { reactRouter } from '@react-router/dev/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
	plugins: [tailwindcss(), reactRouter(), tsconfigPaths()],
	// serverの設定がないとdevcontainer内で開発サーバーを公開できない
	server: {
		host: true,
		port: 5137,
		strictPort: true,
		watch: {
			usePolling: true,
		},
	},
});
