// メールアドレスは前後の空白を除き、小文字にそろえて比べる
export function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

// 管理者かどうか。ADMIN_EMAIL と同じアドレスなら管理者
export function isAdminEmail(email: string, adminEmail: string): boolean {
  return normalizeEmail(email) === normalizeEmail(adminEmail);
}
