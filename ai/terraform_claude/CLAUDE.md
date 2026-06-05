# Terraform コーディング規約
このリポジトリのTerraformコードを生成・編集する際のルールを記載する。
Claude CodeなどのAIエージェントは、以下のルールを厳守すること。

## 命名規則
- すでにある同種のリソース名に準拠すること。

## 開発の遵守事項
- いかなるシークレット情報（パスワード、アクセスキーなど）もコード内にハードコードしない。
- 変更を提案する前に、必ず `terraform fmt` と `terraform validate` を実行し、構文が正しいことを確認すること
- `terraform plan`は対象となる環境のディレクトリ`development`・`staging`・`production`のいずれかの直下のみで実行する
- terraform の AWS 認証コマンド（init/plan/import/refresh/state 等）の実行前に、ログイン中の profile を確認する。SSO 未認証なら `aws sso login` を依頼し、administrator 相当の権限なら誤操作防止のため read-only profile へ切替える（`.claude/settings.json` の PreToolUse hook でも実行時に確認を促す）
- 調査・計画を立てること

## 禁止事項
- 確認なしに勝手にコードの作成・更新・削除をしない
- **`terraform apply` および `terraform destroy` の実行は絶対に禁止**
  - 引数付き・サブコマンド・複合コマンド（`cd ... && terraform apply` 等）・環境変数prefix付き（`AWS_PROFILE=x terraform destroy` 等）を含め、いかなる形でも実行しない
  - state への反映（apply）やリソース削除（destroy）はユーザーが手動で実施する。AIは `terraform plan` までで止めること
  - この禁止は `.claude/settings.json` の `permissions.deny` と `PreToolUse` hook でも二重にブロックしている
- **`provisioner`（`local-exec` / `remote-exec`）内で `terraform apply` / `terraform destroy` を実行する記述を `.tf` に書かない**
  - Bash の deny をすり抜けて手動 apply 時に連鎖実行されるバックドアになるため禁止
  - `.claude/settings.json` の `PreToolUse(Write/Edit/MultiEdit)` hook（`terraform-provisioner-guard.sh`）で書き込み時にブロックしている
- パスワード、APIキー、tokenといった秘密情報は直接回答せずダミーに置換する

# Git規約
- 名前が`development`、`master`、`main`のブランチに対して、直接変更や削除は行わない
- 作業ブランチ作成は、指示がない限りはリポジトリのdefaultブランチをpullしてから行う
- タスク実行前に、必ず作業用ブランチを作成する
- 確認なしにコミット・pushをしない
