import { action, Form, useForm } from "@void/react";
import { LogOut, Trash2 } from "lucide-react";
import { useEffect, useState, type SubmitEvent } from "react";
import { auth } from "void/client";
import { Button } from "../src/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../src/components/ui/card";
import { Input } from "../src/components/ui/input";
import { Label } from "../src/components/ui/label";
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
    <main className="mx-auto flex min-h-screen max-w-sm items-center px-4">
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-xl">{mode === "signIn" ? "ログイン" : "新規登録"}</CardTitle>
          <CardDescription>
            {mode === "signIn"
              ? "Todo を使うにはログインしてください"
              : "招待されたメールアドレスで登録できます"}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={submit} className="grid gap-4">
            {mode === "signUp" && (
              <div className="grid gap-2">
                <Label htmlFor="name">名前</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
              </div>
            )}
            <div className="grid gap-2">
              <Label htmlFor="email">メールアドレス</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="password">パスワード（8文字以上）</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            {notice && <p className="text-sm text-muted-foreground">{notice}</p>}
            <Button type="submit" disabled={pending} className="w-full">
              {mode === "signIn" ? "ログイン" : "登録する"}
            </Button>
          </form>

          <Button
            variant="link"
            className="mt-4 px-0"
            onClick={() => setMode(mode === "signIn" ? "signUp" : "signIn")}
          >
            {mode === "signIn" ? "アカウントを作る" : "ログイン画面に戻る"}
          </Button>
        </CardContent>
      </Card>
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
    <main className="mx-auto max-w-xl px-4 py-10">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Todo</h1>
          <p className="text-sm text-muted-foreground">{userName} さん</p>
        </div>
        <div className="flex items-center gap-2">
          {isAdmin && (
            <Button variant="outline" size="sm" asChild>
              <a href="/admin">招待管理</a>
            </Button>
          )}
          <Button variant="ghost" size="sm" onClick={signOut}>
            <LogOut />
            ログアウト
          </Button>
        </div>
      </header>

      <Card>
        <CardContent className="p-6">
          <Form form={form} className="flex gap-2">
            <Input
              value={form.data.title}
              onChange={(e) => form.setData("title", e.target.value)}
              placeholder="やることを入力"
            />
            <Button type="submit" disabled={form.pending}>
              追加
            </Button>
          </Form>
          {form.errors.title && (
            <p className="mt-2 text-sm text-destructive">{form.errors.title}</p>
          )}

          <ul className="mt-6 divide-y">
            {todos.map((t) => (
              <li key={t.id} className="flex items-center gap-3 py-3">
                <input
                  type="checkbox"
                  className="size-4 accent-primary"
                  checked={t.done}
                  onChange={() => action("/?toggle", { data: { id: t.id, done: !t.done } })}
                />
                <span className={t.done ? "flex-1 text-muted-foreground line-through" : "flex-1"}>
                  {t.title}
                </span>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label="削除"
                  onClick={() => action("/?remove", { data: { id: t.id } })}
                >
                  <Trash2 />
                </Button>
              </li>
            ))}
          </ul>

          {todos.length === 0 && (
            <p className="mt-6 text-center text-sm text-muted-foreground">まだ何もありません</p>
          )}
        </CardContent>
      </Card>
    </main>
  );
}
