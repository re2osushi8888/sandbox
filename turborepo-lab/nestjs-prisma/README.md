# nestjs-prisma

## 実現したいこと
- packagesの中でprismaの型共有を行い、フロントとバックエンドで共有を行う

## 結論
Nestjsとの相性が悪く、諦めることにする

## 理由
- prismaとturborepoの組み合わせは[こちらの資料](https://turbo.build/docs/core-concepts/internal-packages)によるとJust-in-Time Packagesの戦略になる
  - Nestjsとの相性が悪い。一応vite-plugin-nodeを使えばvite上で動かせる。

## 参考文献
- https://www.prisma.io/docs/guides/turborepo
- https://turbo.build/docs/core-concepts/internal-packages
- 
