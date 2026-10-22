import { todos } from "@schema";
import type { InferProps } from "void";
import { defineHandler } from "void/handler";
import { getUser, requireAuth } from "void/auth";
import { and, db, desc, eq } from "void/db";
import { env } from "void/env";
import { z } from "zod";
import { isAdminEmail } from "../src/admin";
import { todoTitleSchema } from "../src/todo";

export type Props = InferProps<typeof loader>;

// GET / — ログイン中なら自分の一覧と管理者かどうか、未ログインなら空の一覧を返す
export const loader = defineHandler(async () => {
  const user = getUser();
  const items = user
    ? await db.select().from(todos).where(eq(todos.userId, user.id)).orderBy(desc(todos.id))
    : [];
  const isAdmin = user !== null && isAdminEmail(user.email, env.ADMIN_EMAIL);
  return { user, isAdmin, todos: items };
});

// POST /?add, /?toggle, /?remove — いずれもログインが必要（未ログインは 401）
// 成功すると loader が再実行されて一覧が更新される
export const actions = {
  add: defineHandler.withValidator({
    body: z.object({
      title: todoTitleSchema,
    }),
  })(async (c, { body }) => {
    const user = requireAuth(c);
    await db.insert(todos).values({ title: body.title, userId: user.id });
  }),

  toggle: defineHandler.withValidator({
    body: z.object({
      id: z.number().int(),
      done: z.boolean(),
    }),
  })(async (c, { body }) => {
    const user = requireAuth(c);
    await db
      .update(todos)
      .set({ done: body.done })
      .where(and(eq(todos.id, body.id), eq(todos.userId, user.id)));
  }),

  remove: defineHandler.withValidator({
    body: z.object({
      id: z.number().int(),
    }),
  })(async (c, { body }) => {
    const user = requireAuth(c);
    await db.delete(todos).where(and(eq(todos.id, body.id), eq(todos.userId, user.id)));
  }),
};
