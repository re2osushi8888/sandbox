import { describe, expect, it } from "vite-plus/test";
import { todoTitleSchema } from "./todo";

describe("todoTitleSchema", () => {
  it("前後の空白を取り除く", () => {
    expect(todoTitleSchema.parse("  牛乳を買う  ")).toBe("牛乳を買う");
  });

  it("空白だけのタイトルは拒否する", () => {
    expect(() => todoTitleSchema.parse("   ")).toThrow();
  });

  it("空文字は拒否する", () => {
    expect(() => todoTitleSchema.parse("")).toThrow();
  });

  it("200文字までは許可する", () => {
    expect(todoTitleSchema.parse("a".repeat(200))).toBe("a".repeat(200));
  });

  it("201文字以上は拒否する", () => {
    expect(() => todoTitleSchema.parse("a".repeat(201))).toThrow();
  });
});
