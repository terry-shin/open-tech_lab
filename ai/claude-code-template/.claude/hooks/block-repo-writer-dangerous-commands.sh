#!/bin/bash
# repo-writer 専用 PreToolUse フック。
# terraform apply/destroy、commit/push 等の破壊的・副作用のあるコマンドを、
# プロンプトの指示だけに頼らず構造的にブロックする。
# BLOCKED_PATTERNS は自組織で使うツールに合わせて追加・削除すること
# （knife / lambroll / rails / rake の行は、それらを使う場合の例）。
set -euo pipefail

INPUT=$(cat)
COMMAND=$(jq -r '.tool_input.command // empty' <<<"$INPUT")

if [ -z "$COMMAND" ]; then
  exit 0
fi

BLOCKED_PATTERNS=(
  'terraform([[:space:]]+-[a-zA-Z0-9=_-]+)*[[:space:]]+(apply|destroy)'
  'git[[:space:]]+commit'
  'git[[:space:]]+push'
  'git[[:space:]]+reset[[:space:]]+--hard'
  'git[[:space:]]+branch[[:space:]]+-[dD]([[:space:]]|$)'
  'git[[:space:]]+clean[[:space:]]+-[a-zA-Z]*f'
  # --- 以下はツール固有の例（使わないものは削除してよい） ---
  'knife[[:space:]]'
  'lambroll[[:space:]]+deploy'
  'rails[[:space:]]+db:migrate'
  'rails[[:space:]]+console'
  'rails[[:space:]]+(s|server)([[:space:]]|$)'
  'rake[[:space:]]+db:migrate'
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -iE "$pattern" > /dev/null; then
    reason="repo-writerの安全フックによりブロックされました: コマンドが禁止パターン「${pattern}」に一致しています。repo-writerはdeploy/apply/migrate/commit/push系のコマンドを実行できません。必要な場合はユーザー自身が手動で実行してください。"
    jq -n --arg reason "$reason" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: $reason
      }
    }'
    exit 0
  fi
done

exit 0
