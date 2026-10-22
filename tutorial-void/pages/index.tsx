import { action, Form, useForm } from "@void/react";
import { useEffect, useState, type SubmitEvent } from "react";
import { auth } from "void/client";
import type { Props } from "./index.server";

export default function TodoPage({ user, isAdmin, todos }: Props) {
  if (!user) return <AuthForm />;
  return <TodoList userName={user.name} isAdmin={isAdmin} todos={todos} />;
}

// ログイン / 新規登録フォーム。ログインに成功したら再読み込みして一覧を出す
// 新規登録は招待の有無を表示しない（アカウントの有無を推測させないため）
function AuthForm() {
  const [mode, setMode] = useState<"signIn" | "signUp">("signIn");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(e: SubmitEvent<HTMLFormElement>) {
    e.preventDefault();
    setPending(true);
    setError(null);
    setNotice(null);
    if (mode === "signUp") {
      const result = await auth.signUp.email({ name, email, password });
      setPending(false);
      if (result.error) {
        setError(result.error.message ?? "登録に失敗しました");
        return;
      }
      setNotice("登録を受け付けました。招待されている場合は、ログインしてください。");
      setMode("signIn");
      setPassword("");
      return;
    }
    const result = await auth.signIn.email({ email, password });
    setPending(false);
    if (result.error) {
      setError(result.error.message ?? "ログインに失敗しました");
      return;
    }
    window.location.reload();
  }

  return (
    <main
      style={{ maxWidth: 360, margin: "2rem auto", padding: "0 16px", fontFamily: "sans-serif" }}
    >
      <h1>{mode === "signIn" ? "ログイン" : "新規登録"}</h1>

      <form onSubmit={submit} style={{ display: "grid", gap: 8 }}>
        {mode === "signUp" && (
          <input
            placeholder="名前"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ padding: 8 }}
          />
        )}
        <input
          type="email"
          placeholder="メールアドレス"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{ padding: 8 }}
        />
        <input
          type="password"
          placeholder="パスワード（8文字以上）"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ padding: 8 }}
        />
        <button disabled={pending} style={{ padding: 8 }}>
          {mode === "signIn" ? "ログイン" : "登録する"}
        </button>
      </form>

      {error && <p style={{ color: "crimson" }}>{error}</p>}
      {notice && <p>{notice}</p>}

      <button
        onClick={() => setMode(mode === "signIn" ? "signUp" : "signIn")}
        style={{
          marginTop: 16,
          background: "none",
          border: "none",
          color: "#2563eb",
          cursor: "pointer",
        }}
      >
        {mode === "signIn" ? "アカウントを作る" : "ログイン画面に戻る"}
      </button>
    </main>
  );
}

// 自分の Todo 一覧。追加・完了切り替え・削除は名前付きアクションで行う
function TodoList({
  userName,
  isAdmin,
  todos,
}: {
  userName: string;
  isAdmin: boolean;
  todos: Props["todos"];
}) {
  const form = useForm("/?add", { title: "" });

  // 追加に成功したら入力欄を空にする
  useEffect(() => {
    if (form.wasSuccessful) form.reset("title");
  }, [form.wasSuccessful]);

  async function signOut() {
    await auth.signOut();
    window.location.reload();
  }

  return (
    <main
      style={{ maxWidth: 480, margin: "2rem auto", padding: "0 16px", fontFamily: "sans-serif" }}
    >
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>Todo</h1>
        <div>
          <span style={{ marginRight: 8 }}>{userName} さん</span>
          {isAdmin && (
            <a href="/admin" style={{ marginRight: 8 }}>
              招待管理
            </a>
          )}
          <button onClick={signOut}>ログアウト</button>
        </div>
      </header>

      <Form form={form}>
        <input
          value={form.data.title}
          onChange={(e) => form.setData("title", e.target.value)}
          placeholder="やることを入力"
          style={{ width: "70%", padding: 8 }}
        />
        <button disabled={form.pending} style={{ padding: 8, marginLeft: 8 }}>
          追加
        </button>
        {form.errors.title && <p style={{ color: "crimson" }}>{form.errors.title}</p>}
      </Form>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {todos.map((t) => (
          <li
            key={t.id}
            style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 0" }}
          >
            <input
              type="checkbox"
              checked={t.done}
              onChange={() => action("/?toggle", { data: { id: t.id, done: !t.done } })}
            />
            <span style={{ flex: 1, textDecoration: t.done ? "line-through" : "none" }}>
              {t.title}
            </span>
            <button onClick={() => action("/?remove", { data: { id: t.id } })}>削除</button>
          </li>
        ))}
      </ul>

      {todos.length === 0 && <p>まだ何もありません</p>}
    </main>
  );
}
