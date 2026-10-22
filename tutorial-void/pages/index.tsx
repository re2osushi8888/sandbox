import { action, Form, useForm } from "@void/react";
import { useEffect } from "react";
import type { Props } from "./index.server";

export default function TodoPage({ todos }: Props) {
  const form = useForm("/?add", { title: "" });

  // 追加に成功したら入力欄を空にする
  useEffect(() => {
    if (form.wasSuccessful) form.reset("title");
  }, [form.wasSuccessful]);

  return (
    <main
      style={{ maxWidth: 480, margin: "2rem auto", padding: "0 16px", fontFamily: "sans-serif" }}
    >
      <h1>Todo</h1>

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
