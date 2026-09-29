# Claude Code 設定テンプレート

チームの「作業ポータル」となるリポジトリに Claude Code を導入するための、設定一式とドキュメントの雛形。
あるリポジトリで運用していた構成から、組織固有の文言・設定を取り除き、`<...>` 形式のプレースホルダに置き換えたもの。

## 構成

```
.
├── .mcp.json                  # MCPサーバー（aws-mcp / playwright）
├── .claude/
│   ├── CLAUDE.md              # プロジェクト規約（Git・PR規約、文書スタイル、用語集 等）
│   ├── settings.json          # 最小権限の許可リスト、defaultMode: plan
│   ├── hooks/                 # repo-writer 用の破壊的コマンドブロックフック
│   ├── agents/                # サブエージェント（調査・実装代行・レビュー・検証・issue処理）
│   └── skills/                # スキル（ユーザー起動用と、エージェント内部用の共通手順）
└── docs/ClaudeCode/           # 利用者向けドキュメント（設計意図、初期設定、一覧、eval fixture）
```

各エージェント・スキルの役割は [docs/ClaudeCode/agents-and-skills.md](./docs/ClaudeCode/agents-and-skills.md) を参照。

## 導入手順

1. `.claude/`・`.mcp.json`・`docs/ClaudeCode/` を、ポータルにするリポジトリへコピーする
2. 下記「プレースホルダ一覧」の値を、`grep -rn '<[A-Z_]*>' .` 等で洗い出して置き換える
   - `<REPO_NAME>` と「実行時に埋まる値」は置き換えない（`example-analyzer.md` を雛形として残すため）
3. 調査したいリポジトリごとに `.claude/agents/example-analyzer.md` をコピーして `<repo>-analyzer.md` を作り、コピー先で `<REPO_NAME>` 等を置き換える
   - 記入例: `app-analyzer.md`（アプリケーション）、`terraform-analyzer.md`（IaC）
   - 記入例を削除する場合は、`grep -rn -E 'app-analyzer|terraform-analyzer|app-repo-path|terraform-repo-path' .` で参照箇所を洗い出して直す（repo-writer・code-reviewer の対応リポジトリ一覧、issue-worker・aws-resource-investigator の委譲先、`agents-and-skills.md`、`evals/` 等）
4. `repo-writer.md` と `code-reviewer.md` の「対応リポジトリ一覧」に、作った analyzer に対応する行を追加する
5. `issue-worker.md` などで委譲先として列挙している analyzer 名を、実際に作ったものに合わせる
6. `.claude/hooks/block-repo-writer-dangerous-commands.sh` の `BLOCKED_PATTERNS` を、使っているツールに合わせて調整する
7. `docs/ClaudeCode/agents-and-skills.md` の一覧を、実際の構成に合わせて更新する

## プレースホルダ一覧

| プレースホルダ | 意味 | 主な出現箇所 |
|---|---|---|
| `<AI_TASK_LABEL>` | issue-worker が処理対象にする issue ラベル名（例: `AIタスク`） | CLAUDE.md、issue-worker.md、docs |
| `<COMPANY>` / `<TEAM_NAME>` | 組織名・チーム名 | CLAUDE.md |
| `<DEFAULT_BRANCH>` | ポータルリポジトリのデフォルトブランチ名 | CLAUDE.md、issue-worker.md、analyzer-agent-refresh |
| `<DEFAULT_REGION>` | AWS調査時のデフォルトリージョン | aws-resource-investigator.md、issue-worker.md |
| `<GITHUB_ORG>` / `<PORTAL_REPO>` | ポータルリポジトリの GitHub org 名・リポジトリ名 | CLAUDE.md、各エージェント、docs |
| `<MONITORING_SERVICE>` / `<SLACK_CHANNEL>` | 連携している外部サービス | CLAUDE.md |
| `<PROD_ACCOUNT_ID>` 等 | 環境ごとの AWS アカウントID（PROD / STG / DEV / OPS） | CLAUDE.md、terraform-analyzer.md |
| `<PROD_ALIAS>` 等 | 環境を指す社内の呼び名（用語集で使う） | CLAUDE.md |
| `<PROD_PROFILE>` 等 | 環境ごとの読み取り専用 AWS CLI プロファイル名 | .mcp.json、CLAUDE.md、getting-started.md |
| `<REPO_NAME>` / `<product>` 等（小文字） | analyzer 雛形・記入例の中の説明用の値 | example-analyzer.md、記入例 |

### 置き換え不要（実行時に埋まる値）

以下はエージェントやスキルが実行時に値を決める表記であり、置き換えない。

- `<PATH_FILE>` / `<REPO_LABEL>` / `<TARGET_REPO>`（エージェントのパラメータ・変数）
- `<対象プロファイル名>` のような日本語入りの `<...>`

## 任意で外せるもの

- **AWS 連携**: 使わない場合は次を削除する
  - `.mcp.json` の `aws-mcp`
  - `aws-resource-investigator.md`、`aws-monthly-cost-review/`
  - CLAUDE.md の「用語集」「aws-mcp 利用時の注意事項」、getting-started.md の SSO セクション
  - 各エージェント内の `aws-resource-investigator` への言及
- **issue 起点の作業**: 使わない場合は `issue-worker.md` と `ai-task-issue-workflow.md`、CLAUDE.md の該当行を削除する
- **playwright**: ブラウザ操作が不要なら `.mcp.json` から削除する

## 設計上のポイント

- 調査系エージェントは読み取り専用。書き込みは `repo-writer` に限定し、独立した git worktree 上で行う。commit 以降は人が行う
- 破壊的コマンドはプロンプトの指示だけでなく、`PreToolUse` フックでも構造的にブロックする
- 報告は出力前に `report-verifier`（調査系とは別モデル）が敵対的に検証する。呼び出しは1件につき最大2回（無限ループ防止）
- エージェントの相互呼び出しでは、呼び出し先に自分を再度呼ばせない（無限ループ防止）
- `settings.json` は個別コマンド単位の最小権限。個人の `settings.local.json` は定期的に棚卸しする
