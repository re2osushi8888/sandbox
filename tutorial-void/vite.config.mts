import { defineConfig } from "vite-plus";
import { voidPlugin } from "void";
import { voidReact } from "@void/react/plugin";

export default defineConfig({
  plugins: [voidPlugin(), voidReact()],

  // lint（oxlint）: 生成ファイルは対象外
  lint: {
    ignorePatterns: [".void/**", "dist/**", "db/migrations/**"],
  },

  // format（oxfmt）: 生成ファイルは対象外
  fmt: {
    ignorePatterns: [".void/**", "dist/**", "db/migrations/**", "AGENTS.md", "pnpm-lock.yaml"],
  },
});
