import { invites } from "../db/schema.ts";
import { db, eq } from "void/db";
import { isAdminEmail, normalizeEmail } from "./admin.ts";

// 新規登録できるか判定する。管理者か招待リストに載っていれば許可、それ以外は理由付きで拒否
export async function checkInvited(
  email: string,
  adminEmail: string,
): Promise<{ error: string } | undefined> {
  const normalized = normalizeEmail(email);
  if (isAdminEmail(normalized, adminEmail)) return undefined;

  const [invite] = await db.select().from(invites).where(eq(invites.email, normalized));
  return invite ? undefined : { error: "このメールアドレスは招待されていません" };
}
