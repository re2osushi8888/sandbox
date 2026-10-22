import { defineAuth } from "void/auth";
import { env } from "void/env";
import { checkInvited } from "./src/invite.ts";

// 新規登録は招待制にする。招待リストか管理者のメールアドレスだけ登録できる
// メール認証の送信はしない。管理者が事前に許可したアドレスだけを通す
export default defineAuth(({ defaults }) => ({
  ...defaults,
  emailAndPassword: {
    ...defaults.emailAndPassword,
    enabled: true,
    // autoSignIn を false にすると、既存アカウントと招待されていないアドレスの
    // 登録は同じ応答（200、token なし）になり、アカウントの有無が推測されない
    autoSignIn: false,
  },
  user: {
    ...defaults.user,
    validateUserInfo: async ({ user, source }) => {
      if (source.action !== "create-user") return undefined;
      const email = typeof user.email === "string" ? user.email : "";
      return checkInvited(email, env.ADMIN_EMAIL);
    },
  },
}));
