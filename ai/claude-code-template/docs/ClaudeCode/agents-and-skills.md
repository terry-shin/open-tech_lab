# 導入済みagent・skill一覧

`.claude/agents/` および `.claude/skills/` に定義されている、<PORTAL_REPO>リポジトリで使えるサブエージェント・スキルの一覧。

## サブエージェント

### リポジトリ調査系（analyzer）

対象リポジトリを読み取り専用で調査する専用エージェント。変更は一切行わず、調査結果のみを報告する。初回起動時にリポジトリのローカルパスをユーザーに質問して設定する（詳細は [getting-started.md](./getting-started.md)）。

| エージェント名 | 対象リポジトリ | 用途 |
|---|---|---|
| `app-analyzer` | `app` | 記入例（アプリケーション）。モジュール構成、WebAPI実装、OpenAPI仕様、ECSデプロイ構成の把握 |
| `example-analyzer` | `<REPO_NAME>` | 新しい analyzer を作るための雛形。コピーしてリポジトリごとに `<repo>-analyzer.md` を作る |
| `terraform-analyzer` | `terraform` | 記入例（IaC）。EC2/ECS/RDS/IAM/SG/LB/S3等のリソース定義把握、環境間差分の追跡 |

### AWS環境調査系

| エージェント名 | 対象 | 用途 |
|---|---|---|
| `aws-resource-investigator` | AWSアカウント環境（リポジトリ非依存） | EC2/ECS/RDS/IAM/SG/LB/S3/Lambda/CloudWatch等の現状把握・設定確認・セキュリティ観点でのレポート。呼び出し前にコーディネーター（親のClaude）がSSO認証等を完了させる前提 |

### 実装代行系（writer）

| エージェント名 | 対象 | 用途 |
|---|---|---|
| `repo-writer` | 「対応リポジトリ一覧」に登録したリポジトリ（例: `app` / `terraform`） | 対象リポジトリへのファイル作成・編集を代行。作業計画は立てず、指示された変更のみを実行する。独立したgit worktree上で作業し、commit/push/PR作成は一切行わずユーザー承認待ちで停止する。`terraform apply` 等の破壊的コマンドはPreToolUseフックで構造的にブロックされる |

### レビュー系（reviewer）

| エージェント名 | 対象 | 用途 |
|---|---|---|
| `code-reviewer` | `repo-writer` と同じリポジトリ ＋ `<PORTAL_REPO>` | Claude Codeが実装したコード変更を、push・PR作成前に読み取り専用でレビューする。`git diff`で変更差分を検出し、対象リポジトリの`*-analyzer`で既存実装との整合性を確認（`<PORTAL_REPO>`はanalyzerなしで直接読み取る）、IaC変更時は任意で`aws-resource-investigator`によるAWS実リソース確認も行う。指摘は「必須修正／推奨／提案」の3段階で返す。`repo-writer`実行時は、diff提示後の呼び出しがステップ6で推奨として案内される |

### 検証・コーディネーター系

| エージェント名 | 用途 |
|---|---|
| `issue-worker` | <PORTAL_REPO>リポジトリのGitHub Issue（「<AI_TASK_LABEL>」ラベル、自分にアサイン済み）を読み取り、内容に応じて調査系エージェントに委譲するコーディネーター。結果は`report-verifier`による検証を経てissueコメントとして投稿する |
| `report-verifier` | 調査系analyzerエージェント・`issue-worker`の最終報告を出力確定前に読み取り専用で検証する。事実claim（`path:line`・リソースID等）の照合、推測の明記漏れ、論理飛躍、秘密情報マスキング漏れ、結論と根拠の不整合を検出する。無限ループ防止のため自身は他のサブエージェントを呼び出さない。調査系エージェント群（`sonnet`）とは異なるモデル（`opus`）で検証することで、単一モデルによる自己レビューに留まらない検証にしている（ただしモデル共通のバイアスまでは排除できない点に留意） |

## スキル

`.claude/skills/` には、ユーザーが直接呼び出すスキルと、エージェントが内部で自動的に使う共通手順の2種類がある。

### ユーザーが明示的に指示して使うスキル

| スキル名 | 用途 |
|---|---|
| `analyzer-agent-refresh` | 調査系エージェント（`*-analyzer`）の定義が対象リポジトリの現在の構成と乖離していないかを棚卸しする。対象リポジトリを`fetch`で最新化し、パス設定の健全性・ディレクトリ構造差分・パス参照の実在性を照合して「実害あり／追記推奨／対応不要」に分類する。編集とPR作成はユーザー承認後にのみ行う |
| `aws-monthly-cost-review` | AWS環境（本番/STG/開発/運用）のサービス別コストを月単位で比較し、増減の大きいサービスを特定する。差額$500以上または増減率30%以上のサービスのみ`aws-resource-investigator`に深掘り調査を自動委譲する。`/loop`の7日失効制約により定期自動実行は非対応、ユーザーの手動起動を前提とする |

### エージェントが内部で使う共通手順（`user-invocable: false`）

ユーザーが直接呼び出すものではなく、analyzer系エージェント等が調査・報告の過程で必ず実行する内部手順。

| スキル名 | 用途 |
|---|---|
| `repo-path-resolution` | 調査対象リポジトリのローカルパスを `~/.claude/<PATH_FILE>` から解決する共通手順。未設定時は初回セットアップを案内する |
| `report-verifier-protocol` | 調査結果・報告文のドラフトを出力確定前に `report-verifier` へ検証依頼する共通手順。1件のドラフトにつき最大2回までという呼び出し上限を規定する（無限ループ防止） |

## MCPサーバー

`.mcp.json` に設定されているMCPサーバーの一覧。

| サーバー名 | 概要 |
|---|---|
| `aws-mcp` | AWSリソースの読み取り専用調査（mcp-proxy-for-aws経由）。プロファイルの詳細は [getting-started.md](./getting-started.md) を参照 |
| `playwright` | ブラウザ自動化・スクリーンショット取得 |

## 権限設定（settings.json / settings.local.json）の棚卸し

`.claude/settings.json`（コミット済み）は個別コマンド単位の最小権限方針で許可リストを構成している。
一方 `.claude/settings.local.json`（gitignore対象・ローカルのみ）は、Claude Codeの「選択を記憶」機能に
より使用の都度、承認内容が自然に蓄積していく。放置すると `Bash(git *)` のような広範なワイルドカード
許可が増え、当初の最小権限方針から実質的に乖離していく（`Bash` の場合は破壊的なサブコマンドまで
無条件許可してしまうリスクがある）。

四半期に一度を目安に、`settings.local.json` の許可リストを `settings.json` の最小権限方針と照らして
棚卸しする（広範なワイルドカードを安全な部分集合に絞り込む、セッション固有で再利用不可能になった
エントリを削除する等）。棚卸し作業には `update-config` スキルを利用する。

## eval fixture

`report-verifier` の検証ロジックや `repo-writer` の拒否ロジックがプロンプトドリフトで劣化していない
かを確認するための軽量なfixtureを [evals/README.md](./evals/README.md) に用意している。該当エージェント
定義を変更した際、または四半期に一度を目安に手動で流して動作確認する。

## 次に読むもの

- 全体の設計意図: [overview.md](./overview.md)
- 使い始める前の準備: [getting-started.md](./getting-started.md)
- エージェントのeval fixture: [evals/README.md](./evals/README.md)
