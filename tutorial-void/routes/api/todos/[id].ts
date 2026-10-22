import { todos } from "@schema";
import { defineHandler } from "void";
import { requireAuth } from "void/auth";
import { and, db, eq } from "void/db";
import { z } from "zod";
import { todoTitleSchema } from "../../../src/todo";

const idParams = z.object({
  id: z.coerce.number().int().positive(),
});

const updateTodoBody = z.object({
  title: todoTitleSchema.optional(),
  done: z.boolean().optional(),
});

// 他人の Todo は存在しない扱い（404）にする。所有者チェックは id と userId の両方で行う

// GET /api/todos/:id — 自分の1件を取得
export const GET = defineHandler.withValidator({
  params: idParams,
})(async (c, { params }) => {
  const user = requireAuth(c);
  const [todo] = await db
    .select()
    .from(todos)
    .where(and(eq(todos.id, params.id), eq(todos.userId, user.id)));
  if (!todo) return c.json({ error: "Todo not found" }, 404);
  return todo;
});

// PATCH /api/todos/:id — 自分の Todo を部分更新（title / done のどちらか、または両方）
export const PATCH = defineHandler.withValidator({
  params: idParams,
  body: updateTodoBody,
})(async (c, { params, body }) => {
  const user = requireAuth(c);
  const changes: { title?: string; done?: boolean } = {};
  if (body.title !== undefined) changes.title = body.title;
  if (body.done !== undefined) changes.done = body.done;
  if (Object.keys(changes).length === 0) {
    return c.json({ error: "No fields to update" }, 400);
  }

  const [updated] = await db
    .update(todos)
    .set(changes)
    .where(and(eq(todos.id, params.id), eq(todos.userId, user.id)))
    .returning();
  if (!updated) return c.json({ error: "Todo not found" }, 404);
  return updated;
});

// DELETE /api/todos/:id — 自分の Todo を削除。成功時は 204 No Content
export const DELETE = defineHandler.withValidator({
  params: idParams,
})(async (c, { params }) => {
  const user = requireAuth(c);
  const [deleted] = await db
    .delete(todos)
    .where(and(eq(todos.id, params.id), eq(todos.userId, user.id)))
    .returning({ id: todos.id });
  if (!deleted) return c.json({ error: "Todo not found" }, 404);
  return c.body(null, 204);
});
