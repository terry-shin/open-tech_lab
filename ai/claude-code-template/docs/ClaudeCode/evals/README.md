# エージェントのeval fixture

`report-verifier` の検証ロジックと `repo-writer` の拒否ロジックが、エージェント定義の変更（プロンプト
ドリフト）によって劣化していないかを確認するための軽量なfixture集。CI等での自動実行は行わず、
手動でClaude Code上から実行することを前提にしている。

## 対象

- **report-verifier**: 報告文ドラフトの敵対的検証ロジック（[report-verifier-cases.md](./report-verifier-cases.md)）
- **repo-writer**: ホワイトリスト外リポジトリ・破壊的コマンドに対する拒否ロジック（[repo-writer-cases.md](./repo-writer-cases.md)）

## 実行方法

1. 対象のfixtureファイル（`report-verifier-cases.md` または `repo-writer-cases.md`）を開き、
   各ケースの「入力」をそのまま該当エージェントへの `Agent` ツール呼び出しのプロンプトとして渡す
   （`report-verifier` の場合は `REPORT_DRAFT` と `CONTEXT` として渡す）。
2. 実際の出力を、各ケースの「期待される結果」と目視で照合する。
3. 期待と異なる結果が出た場合、直近の該当エージェント定義（`.claude/agents/report-verifier.md` /
   `.claude/agents/repo-writer.md`）の変更点を確認し、意図した仕様変更か、プロンプトドリフトによる
   劣化かを判断する。

## 推奨実行タイミング

- `report-verifier.md` / `repo-writer.md` の定義を変更した直後
- 上記変更がなくても、四半期に一度を目安に（[agents-and-skills.md](../agents-and-skills.md) の
  権限棚卸しと合わせて実施すると効率的）
