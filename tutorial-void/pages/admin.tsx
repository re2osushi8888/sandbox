import { action, Form, useForm } from "@void/react";
import { ArrowLeft, Trash2 } from "lucide-react";
import { Button } from "../src/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../src/components/ui/card";
import { Input } from "../src/components/ui/input";
import type { Props } from "./admin.server";

export default function AdminPage({ isAdmin, invites }: Props) {
  return (
    <main className="mx-auto max-w-xl px-4 py-10">
      <header className="mb-8 flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">招待管理</h1>
        <Button variant="ghost" size="sm" asChild>
          <a href="/">
            <ArrowLeft />
            トップへ
          </a>
        </Button>
      </header>

      {!isAdmin ? (
        <Card>
          <CardContent className="p-6 text-sm text-muted-foreground">
            管理者としてログインしてください。
          </CardContent>
        </Card>
      ) : (
        <InviteList invites={invites} />
      )}
    </main>
  );
}

// 招待メールアドレスの追加と取り消し。登録できるのはここに載っているアドレスだけ
function InviteList({ invites }: { invites: Props["invites"] }) {
  const form = useForm("/admin?add", { email: "" });

  return (
    <Card>
      <CardHeader>
        <CardTitle>招待したメールアドレス</CardTitle>
        <CardDescription>ここに載っているアドレスだけ新規登録できます</CardDescription>
      </CardHeader>
      <CardContent className="grid gap-6">
        <Form form={form} className="flex gap-2">
          <Input
            type="email"
            value={form.data.email}
            onChange={(e) => form.setData("email", e.target.value)}
            placeholder="招待するメールアドレス"
          />
          <Button type="submit" disabled={form.pending}>
            招待
          </Button>
        </Form>
        {form.errors.email && <p className="text-sm text-destructive">{form.errors.email}</p>}

        <ul className="divide-y">
          {invites.map((inv) => (
            <li key={inv.email} className="flex items-center gap-3 py-3">
              <span className="flex-1 text-sm">{inv.email}</span>
              <Button
                variant="ghost"
                size="icon"
                aria-label="取り消し"
                onClick={() => action("/admin?remove", { data: { email: inv.email } })}
              >
                <Trash2 />
              </Button>
            </li>
          ))}
        </ul>

        {invites.length === 0 && (
          <p className="text-center text-sm text-muted-foreground">招待中のアドレスはありません</p>
        )}
      </CardContent>
    </Card>
  );
}
