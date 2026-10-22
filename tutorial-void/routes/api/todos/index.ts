import { todos } from "@schema";
import { defineHandler } from "void";
import { db, desc } from "void/db";
import { z } from "zod";
import { todoTitleSchema } from "../../../src/todo";

const createTodoBody = z.object({
  title: todoTitleSchema,
});

// GET /api/todos — 一覧（新しい順）
export const GET = defineHandler(async () => {
  return db.select().from(todos).orderBy(desc(todos.id));
});

// POST /api/todos — 作成。成功時は 201 Created
export const POST = defineHandler.withValidator({
  body: createTodoBody,
})(async (c, { body }) => {
  const [created] = await db.insert(todos).values({ title: body.title }).returning();
  return c.json(created, 201);
});
