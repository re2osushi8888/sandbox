import { defineEnv, email } from "void/env";

export default defineEnv({
  // 管理者のメールアドレス。招待リストに関係なく登録でき、/admin で招待を管理できる
  ADMIN_EMAIL: email(),
});
