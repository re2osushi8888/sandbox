import { defineConfig } from "vite-plus";

// テストは対象ファイルと同じディレクトリに *.test.ts(x) として置く
// Void のプラグインは読み込まない（純粋なロジックのテストに不要で、起動エラーになるため）
export default defineConfig({
  test: {
    include: ["**/*.test.{ts,tsx}"],
    exclude: ["node_modules/**", "dist/**", ".void/**"],
  },
});
