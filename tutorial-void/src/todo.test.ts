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
});
