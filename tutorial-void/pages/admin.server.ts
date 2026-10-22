import { invites } from "@schema";
import type { InferProps } from "void";
import { defineHandler } from "void/handler";
import { getUser, requireAuth } from "void/auth";
import { db, desc, eq } from "void/db";
import { env } from "void/env";
import { z } from "zod";
import { isAdminEmail, normalizeEmail } from "../src/admin";

export type Props = InferProps<typeof loader>;

// GET /admin — 管理者なら招待リストを返す。管理者でなければ空
export const loader = defineHandler(async () => {
  const user = getUser();
  const isAdmin = user !== null && isAdminEmail(user.email, env.ADMIN_EMAIL);
  const list = isAdmin ? await db.select().from(invites).orderBy(desc(invites.createdAt)) : [];
  return { isAdmin, invites: list };
});

// POST /admin?add, /admin?remove — 管理者だけが実行できる（それ以外は 403）
export const actions = {
  add: defineHandler.withValidator({
    body: z.object({
      email: z.email({ message: "メールアドレスの形式が正しくありません" }),
    }),
  })(async (c, { body }) => {
    const user = requireAuth(c);
    if (!isAdminEmail(user.email, env.ADMIN_EMAIL)) return c.json({ error: "Forbidden" }, 403);
    await db
      .insert(invites)
      .values({ email: normalizeEmail(body.email) })
      .onConflictDoNothing();
    return undefined;
  }),

  remove: defineHandler.withValidator({
    body: z.object({
      email: z.string(),
    }),
  })(async (c, { body }) => {
    const user = requireAuth(c);
    if (!isAdminEmail(user.email, env.ADMIN_EMAIL)) return c.json({ error: "Forbidden" }, 403);
    await db.delete(invites).where(eq(invites.email, normalizeEmail(body.email)));
    return undefined;
  }),
};
