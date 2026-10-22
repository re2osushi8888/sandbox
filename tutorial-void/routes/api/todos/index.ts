import { todos } from "@schema";
import { defineHandler } from "void";
import { requireAuth } from "void/auth";
import { db, desc, eq } from "void/db";
import { z } from "zod";
import { todoTitleSchema } from "../../../src/todo";

const createTodoBody = z.object({
  title: todoTitleSchema,
});

// GET /api/todos — 自分の一覧（新しい順）
export const GET = defineHandler(async (c) => {
  const user = requireAuth(c);
  return db.select().from(todos).where(eq(todos.userId, user.id)).orderBy(desc(todos.id));
});

// POST /api/todos — 自分の Todo を作成。成功時は 201 Created
export const POST = defineHandler.withValidator({
  body: createTodoBody,
})(async (c, { body }) => {
  const user = requireAuth(c);
  const [created] = await db
    .insert(todos)
    .values({ title: body.title, userId: user.id })
    .returning();
  return c.json(created, 201);
});
