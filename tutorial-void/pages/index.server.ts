import { todos } from "@schema";
import type { InferProps } from "void";
import { defineHandler } from "void/handler";
import { db, desc, eq } from "void/db";
import { z } from "zod";
import { todoTitleSchema } from "../src/todo";

export type Props = InferProps<typeof loader>;

// GET / — 一覧を新しい順に返す
export const loader = defineHandler(async () => {
  const items = await db.select().from(todos).orderBy(desc(todos.id));
  return { todos: items };
});

// POST /?add, /?toggle, /?remove
// 成功すると loader が再実行されて一覧が更新される
export const actions = {
  add: defineHandler.withValidator({
    body: z.object({
      title: todoTitleSchema,
    }),
  })(async (_c, { body }) => {
    await db.insert(todos).values({ title: body.title });
  }),

  toggle: defineHandler.withValidator({
    body: z.object({
      id: z.number().int(),
      done: z.boolean(),
    }),
  })(async (_c, { body }) => {
    await db.update(todos).set({ done: body.done }).where(eq(todos.id, body.id));
  }),

  remove: defineHandler.withValidator({
    body: z.object({
      id: z.number().int(),
    }),
  })(async (_c, { body }) => {
    await db.delete(todos).where(eq(todos.id, body.id));
  }),
};
