# study-ts-elevator
TSでElevatorを作成してみる。cucumberを使ってBDDでやってみる

## playwright
### 依存関係のライブラリがまだインストールできてないので暫定対応コマンド
```
$ bunx playwright install-deps
```

### test実行
```
$ bun run ptest // playwright test実行
or
$ bunx playwright test --reporter list
```

### codegen
```
$ bunx playwright codegen http://localhost:3000
```

## cucumber
### test実行
```
$ bun run ctest
```

### テスト結果のレポートを出す方法
以下のコマンドを実行し、Reportページが出るURLをブラウザで開く
```
$ bun run ctest --publish
```

## メモ
featureファイルは日本語もいけるので日本語でもいいかも
