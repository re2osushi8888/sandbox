import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// shadcn/ui のユーティリティ。クラス名を結合し、Tailwind の競合を解決する
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
