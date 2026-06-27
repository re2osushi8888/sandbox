# Go 文法メモ — 美しい庭問題で使ったもの

写経用。上から順に読むと文法が積み上がるように並べてある。

---

## 1. パッケージとエントリポイント

```go
package main  // このファイルが属するパッケージ名

func main() { // package main にだけ書ける。プログラムの起動点
    // ...
}
```

- すべての `.go` ファイルの先頭に `package 名前` が必要
- 実行可能プログラムは必ず `package main` + `func main()`
- テストファイルも同じ `package main` に置いてよい

---

## 2. 関数

```go
// 引数: 名前 型  戻り値: 型
func minCuts(heights []int) int {
    return 0
}

// 複数の引数
func countCuts(heights []int, startHigh bool) int {
    return 0
}
```

TypeScriptとの対応:

```ts
function minCuts(heights: number[]): number { return 0 }
```

```go
func minCuts(heights []int) int { return 0 }
```

- 型は名前の**後ろ**に書く
- 戻り値の型は引数リストの**後ろ**に書く
- `return` は必須（暗黙の return はない）

---

## 3. 変数宣言と `:=`

```go
a := countCuts(heights, true)   // 型推論で宣言 + 代入
b := countCuts(heights, false)

var total int  // 明示的な宣言（初期値は 0）
total = 10

var flag bool  // false で初期化される
```

- `:=` は初回の宣言と代入を同時にやる（型は推論）
- `var` は明示的に型を書く場合や、関数の外（グローバル）で使う
- Goは **宣言した変数を使わないとコンパイルエラー**になる

---

## 4. スライス（配列）

```go
// スライスリテラル
heights := []int{5, 4, 3}

// make でゼロ値スライスを作る
h := make([]int, len(heights))   // [0, 0, 0]
cut := make([]bool, len(heights)) // [false, false, false]

// コピー
copy(h, heights)  // heights の中身を h に複製

// 長さ
len(h)

// インデックスアクセス
h[0]
h[i+1]
```

TypeScriptとの対応:

| TypeScript | Go |
|---|---|
| `number[]` | `[]int` |
| `arr.length` | `len(arr)` |
| `[...arr]` | `make + copy` |
| `arr[0]` | `arr[0]` |

- Goのスライスは参照型。関数に渡すとき変更されたくない場合は `copy` で複製する

---

## 5. if 文

```go
if len(heights) <= 1 {
    return 0
}

if a < b {
    return a
}
return b
```

- 条件式を `()` で囲まない（囲んでもよいが慣習的に書かない）
- `{}` は必須
- Goには三項演算子 `? :` がない → `if-else` で書く

---

## 6. for ループ

```go
// C スタイル（インデックス付き）
for i := 0; i < len(h)-1; i++ {
    // i = 0, 1, 2, ...
}

// range（インデックスと値を両方取る）
for i, v := range cut {
    // i = インデックス, v = 値
}

// range（値だけ使う）
for _, c := range cut {
    // _ でインデックスを捨てる
}
```

TypeScriptとの対応:

| TypeScript | Go |
|---|---|
| `for (let i = 0; i < n; i++)` | `for i := 0; i < n; i++` |
| `for (const v of arr)` | `for _, v := range arr` |
| `arr.forEach((v, i) =>` | `for i, v := range arr` |

---

## 7. bool 型と演算子

```go
iIsHigh := (i%2 == 0) == startHigh
```

- `%` は剰余
- `==` は等値比較（bool 同士も比較できる）
- この式の意味:
  - `i%2 == 0` → i が偶数なら `true`
  - `== startHigh` → startHigh と同じ値なら `true`
  - つまり「偶数インデックス && startHigh=true」または「奇数インデックス && startHigh=false」のとき `true`

---

## 8. テストの書き方

```go
package main

import "testing"

func TestMinCuts(t *testing.T) {
    got := minCuts([]int{5, 4, 3})
    if got != 1 {
        t.Errorf("minCuts([5,4,3]) = %d, want 1", got)
    }
}
```

- ファイル名は `_test.go` で終わる必要がある
- 関数名は `Test` で始める必要がある
- `t.Errorf` でテスト失敗を報告（実行は続く）
- `t.Fatalf` は失敗後にそのテストを中断する

### テーブルドリブンテスト（複数ケースを一括管理）

```go
func TestMinCuts(t *testing.T) {
    tests := []struct {   // 無名構造体のスライス
        name  string
        input []int
        want  int
    }{
        {"already H,L,H", []int{5, 3, 5}, 0},
        {"H,L,L",         []int{5, 4, 3}, 1},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {  // サブテスト
            got := minCuts(tt.input)
            if got != tt.want {
                t.Errorf("minCuts(%v) = %d, want %d", tt.input, got, tt.want)
            }
        })
    }
}
```

- `struct { ... }` は無名構造体（その場でフィールドを定義）
- `[]struct{ ... }{{ ... }, { ... }}` でスライスとして初期化
- `t.Run("名前", func)` でサブテストを作ると失敗時に名前が表示される
- Goで最もよく使われるテストパターン

### テスト実行コマンド

```sh
go test .              # カレントディレクトリ
go test ./...          # 以下すべて再帰的に
go test -v .           # 詳細表示（テスト名が出る）
go test -run TestMinCuts .           # 関数名で絞る
go test -run TestMinCuts/two_same .  # サブテスト名で絞る
```

---

## 9. fmt.Errorf のフォーマット記号

```go
t.Errorf("minCuts(%v) = %d, want %d", tt.input, got, tt.want)
```

| 記号 | 意味 | 例 |
|---|---|---|
| `%d` | 整数 | `42` |
| `%s` | 文字列 | `"hello"` |
| `%v` | 何でも（デフォルト形式） | `[5 4 3]` |
| `%T` | 型名 | `[]int` |

---

## 10. 今回のコード全体

### garden.go

```go
package main

func minCuts(heights []int) int {
    if len(heights) <= 1 {
        return 0
    }
    a := countCuts(heights, true)
    b := countCuts(heights, false)
    if a < b {
        return a
    }
    return b
}

func countCuts(heights []int, startHigh bool) int {
    h := make([]int, len(heights))
    copy(h, heights)

    cut := make([]bool, len(heights))

    for i := 0; i < len(h)-1; i++ {
        iIsHigh := (i%2 == 0) == startHigh

        if iIsHigh {
            if h[i] <= h[i+1] {
                cut[i+1] = true
                h[i+1] = h[i] - 1
            }
        } else {
            if h[i] >= h[i+1] {
                cut[i] = true
                h[i] = h[i+1] - 1
            }
        }
    }

    total := 0
    for _, c := range cut {
        if c {
            total++
        }
    }
    return total
}
```

### garden_test.go

```go
package main

import "testing"

func TestMinCuts(t *testing.T) {
    tests := []struct {
        name  string
        input []int
        want  int
    }{
        {"already H,L,H",  []int{5, 3, 5},       0},
        {"H,L,L",          []int{5, 4, 3},        1},
        {"L,H,H",          []int{3, 4, 5},        1},
        {"H,L,H,H,H",      []int{5, 4, 5, 6, 7},  1},
        {"H,L,H,H,H,H",    []int{5, 4, 5, 6, 7, 8}, 2},
        {"H,E,H",          []int{3, 3, 4},        1},
        {"H,E,E",          []int{3, 3, 2},        1},
        {"empty",          []int{},               0},
        {"single",         []int{5},              0},
        {"two asc",        []int{3, 5},           0},
        {"two desc",       []int{5, 3},           0},
        {"two same",       []int{5, 5},           1},
        {"already L,H,L",  []int{3, 5, 3},        0},
        {"all same",       []int{3, 3, 3, 3},     2},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := minCuts(tt.input)
            if got != tt.want {
                t.Errorf("minCuts(%v) = %d, want %d", tt.input, got, tt.want)
            }
        })
    }
}
```
