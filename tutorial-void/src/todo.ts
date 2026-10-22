import { z } from "zod";

// Todo のタイトル。前後の空白を取り除き、空になるものと 200 文字を超えるものは拒否する
// 画面（named actions）と REST API の両方で使う
export const todoTitleSchema = z
  .string()
  .trim()
  .min(1, { message: "タイトルを入力してください" })
  .max(200, { message: "タイトルは200文字以内で入力してください" });
