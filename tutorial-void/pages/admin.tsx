import { action, Form, useForm } from "@void/react";
import type { Props } from "./admin.server";

export default function AdminPage({ isAdmin, invites }: Props) {
  return (
    <main
      style={{ maxWidth: 480, margin: "2rem auto", padding: "0 16px", fontFamily: "sans-serif" }}
    >
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>招待管理</h1>
        <a href="/">トップへ</a>
      </header>

      {!isAdmin ? <p>管理者としてログインしてください。</p> : <InviteList invites={invites} />}
    </main>
  );
}

// 招待メールアドレスの追加と削除。登録できるのはここに載っているアドレスだけ
function InviteList({ invites }: { invites: Props["invites"] }) {
  const form = useForm("/admin?add", { email: "" });

  return (
    <>
      <Form form={form}>
        <input
          type="email"
          value={form.data.email}
          onChange={(e) => form.setData("email", e.target.value)}
          placeholder="招待するメールアドレス"
          style={{ width: "70%", padding: 8 }}
        />
        <button disabled={form.pending} style={{ padding: 8, marginLeft: 8 }}>
          招待
        </button>
        {form.errors.email && <p style={{ color: "crimson" }}>{form.errors.email}</p>}
      </Form>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {invites.map((inv) => (
          <li
            key={inv.email}
            style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 0" }}
          >
            <span style={{ flex: 1 }}>{inv.email}</span>
            <button onClick={() => action("/admin?remove", { data: { email: inv.email } })}>
              取り消し
            </button>
          </li>
        ))}
      </ul>

      {invites.length === 0 && <p>招待中のアドレスはありません</p>}
    </>
  );
}
