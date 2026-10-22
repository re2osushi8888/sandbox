import { todos } from "@schema";
import { defineHandler } from "void";
import { db, eq } from "void/db";
import { z } from "zod";
import { todoTitleSchema } from "../../../src/todo";

const idParams = z.object({
  id: z.coerce.number().int().positive(),
});

const updateTodoBody = z.object({
  title: todoTitleSchema.optional(),
  done: z.boolean().optional(),
});

// GET /api/todos/:id — 1件取得
export const GET = defineHandler.withValidator({
  params: idParams,
})(async (c, { params }) => {
  const [todo] = await db.select().from(todos).where(eq(todos.id, params.id));
  if (!todo) return c.json({ error: "Todo not found" }, 404);
  return todo;
});

// PATCH /api/todos/:id — 部分更新（title / done のどちらか、または両方）
export const PATCH = defineHandler.withValidator({
  params: idParams,
  body: updateTodoBody,
})(async (c, { params, body }) => {
  const changes: { title?: string; done?: boolean } = {};
  if (body.title !== undefined) changes.title = body.title;
  if (body.done !== undefined) changes.done = body.done;
  if (Object.keys(changes).length === 0) {
    return c.json({ error: "No fields to update" }, 400);
  }

  const [updated] = await db.update(todos).set(changes).where(eq(todos.id, params.id)).returning();
  if (!updated) return c.json({ error: "Todo not found" }, 404);
  return updated;
});

// DELETE /api/todos/:id — 削除。成功時は 204 No Content
export const DELETE = defineHandler.withValidator({
  params: idParams,
})(async (c, { params }) => {
  const [deleted] = await db
    .delete(todos)
    .where(eq(todos.id, params.id))
    .returning({ id: todos.id });
  if (!deleted) return c.json({ error: "Todo not found" }, 404);
  return c.body(null, 204);
});
