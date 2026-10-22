import "../src/index.css";

// 全ページ共通のレイアウト。Tailwind の CSS をここで読み込む
export default function Layout({ children }: { children: React.ReactNode }) {
  return <div className="min-h-screen bg-background text-foreground antialiased">{children}</div>;
}
