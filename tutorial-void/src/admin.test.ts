import { describe, expect, it } from "vite-plus/test";
import { isAdminEmail, normalizeEmail } from "./admin";

describe("normalizeEmail", () => {
  it("前後の空白を除き、小文字にする", () => {
    expect(normalizeEmail("  Admin@Example.COM ")).toBe("admin@example.com");
  });
});

describe("isAdminEmail", () => {
  it("大文字小文字と空白を無視して一致を判定する", () => {
    expect(isAdminEmail(" Admin@Example.com", "admin@example.com")).toBe(true);
  });

  it("別のアドレスは管理者ではない", () => {
    expect(isAdminEmail("user@example.com", "admin@example.com")).toBe(false);
  });
});
