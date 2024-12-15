# study-ts-elevator
TSでElevatorを作成してみる。cucumberを使ってBDDでやってみる

## playwright
### 依存関係のライブラリがまだインストールできてないので暫定対応コマンド
```
$ bunx playwright install-deps
```

### test実行
```
$ bunx playwright test --reporter list
```

### codegen
```
$ bunx playwright codegen http://localhost:3000
```

## cucumber
### test実行
```
$ bun run e2e-test
```

### テスト結果のレポートを出す方法
以下のコマンドを実行し、Reportページが出るURLをブラウザで開く
```
$ bun run e2e-test --publish
```

## メモ
featureファイルは日本語もいけるので日本語でもいいかも
