import { sql } from "void/db";
import { integer, sqliteTable, text } from "void/schema-d1";

// 招待リスト。ここに登録されたメールアドレスだけが新規登録できる（管理者は除く）
export const invites = sqliteTable("invites", {
  email: text("email").primaryKey(),
  createdAt: text("created_at")
    .notNull()
    .default(sql`(datetime('now'))`),
});

export const todos = sqliteTable("todos", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  // 所有者（Better Auth の user.id）。認証導入前の行は NULL で、誰からも見えない
  userId: text("user_id"),
  title: text("title").notNull(),
  done: integer("done", { mode: "boolean" }).notNull().default(false),
  createdAt: text("created_at")
    .notNull()
    .default(sql`(datetime('now'))`),
});
