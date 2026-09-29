# 初期設定・起動前にやること

<PORTAL_REPO>リポジトリのClaude Codeを使い始める前に、以下2点を準備しておく。

## 1. 調査対象リポジトリをあらかじめcloneしておく

`*-analyzer` 系エージェントは、対象リポジトリをローカルにcloneしてある前提で動作する（`repo-path-resolution` skillによる共通処理）。パスは `~/.claude/<リポジトリ名>-repo-path.txt` に保存され、未設定の場合は初回呼び出し時にディレクトリパスを尋ねられ、以降は自動で読み込まれる。**保存するパスは `~/git/...` ではなく `/Users/<username>/git/...` の絶対パスにすること**（シェル変数に読み込んだ際にチルダが展開されず、調査コマンドが失敗するため）。

調査したいリポジトリは事前に `git clone` しておくとスムーズ。対応リポジトリの一覧は [agents-and-skills.md](./agents-and-skills.md) を参照。

## 2. aws-mcp接続のためのSSOログイン

<!-- AWSを使わない場合はこのセクションを削除する -->

AWS環境の調査（`aws-resource-investigator` エージェントや `aws-mcp` を使う操作全般）には、事前にAWS SSOへのログインが必要。

### 対象プロファイル

`.mcp.json` の `AWS_MCP_PROXY_PROFILES` に設定されている、環境ごとの読み取り専用プロファイル（1番目がデフォルト接続先）。

| 環境 | プロファイル名 |
|---|---|
| 本番環境（デフォルト） | `<PROD_PROFILE>` |
| STG環境 | `<STG_PROFILE>` |
| 開発環境 | `<DEV_PROFILE>` |
| 運用環境 | `<OPS_PROFILE>` |

### ログイン手順

調査したい環境に応じて、対象プロファイルでSSOログインする。

```bash
aws sso login --profile <PROD_PROFILE>   # 本番
aws sso login --profile <STG_PROFILE>    # STG
aws sso login --profile <DEV_PROFILE>    # 開発
aws sso login --profile <OPS_PROFILE>    # 運用
```

環境を切り替えるだけであれば、`aws-mcp` の再接続は不要。ツール呼び出し時に `aws_profile` パラメータで対象プロファイルを指定すればよい。

### 接続エラー時のトラブルシュート

`/mcp reconnect aws-mcp` が失敗する等の接続エラー・認証切れが起きた場合、切り替え先ではなく**デフォルトプロファイル（`<PROD_PROFILE>`）のSSOトークン切れ**が原因であることが多い。

1. まずデフォルトプロファイルのSSOトークンを再ログインする: `aws sso login --profile <PROD_PROFILE>`
2. それでも解消しない場合、調査対象の読み取り専用プロファイルでも同様にログインする
3. `/mcp reconnect aws-mcp` を実行し、aws-mcp接続を再確立する

## 次に読むもの

- 全体の設計意図: [overview.md](./overview.md)
- 導入済みのagent・skill一覧: [agents-and-skills.md](./agents-and-skills.md)
