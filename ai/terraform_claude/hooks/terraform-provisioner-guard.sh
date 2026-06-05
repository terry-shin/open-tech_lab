#!/usr/bin/env bash
# PreToolUse(Write|Edit|MultiEdit) hook:
# .tf / .tf.json へ書き込まれる内容に、provisioner(local-exec/remote-exec) 経由で
# `terraform apply` / `terraform destroy` を実行する記述が含まれていないか検査する。
#
# 背景: Bash の terraform apply/destroy は別 hook と permissions.deny でブロック済みだが、
#       .tf コードに local-exec provisioner を埋め込むと、ユーザーの手動 apply 時に
#       シェル経由で apply/destroy が連鎖実行され、Bash レベルの防御をすり抜ける。
#       本 hook はそのバックドアを書き込み時点でブロックする。
#
# macOS の bash 3.2 でも動くようにし、set -e/-u は使わず jq の失敗は明示的に握る。
# 対象外（.tf 以外 / 非該当）は無出力で exit 0。

input=$(cat)

# 対象ファイルパス（Write/Edit/MultiEdit 共通で .tool_input.file_path）
file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // ""' 2>/dev/null)

# .tf / .tf.json 以外は無干渉
case "$file_path" in
  *.tf|*.tf.json) ;;
  *) exit 0 ;;
esac

# 書き込み候補テキストを抽出して連結:
#  - Write    : .tool_input.content
#  - Edit     : .tool_input.new_string
#  - MultiEdit: .tool_input.edits[].new_string
content=$(printf '%s' "$input" | jq -r '
  [ (.tool_input.content // empty),
    (.tool_input.new_string // empty),
    ((.tool_input.edits // []) | map(.new_string // empty) | .[]) ]
  | join("\n")
' 2>/dev/null)

if [ -z "$content" ]; then
  exit 0
fi

# deny JSON を出力して終了（reason は jq -Rs で安全に文字列化）
deny() {
  reason_json=$(printf '%s' "$1" | jq -Rs .)
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s}}' "$reason_json"
  exit 0
}

# apply/destroy provisioner のシグネチャ: 3要素を同時に含む場合に deny
has_provisioner=$(printf '%s' "$content" | grep -Eqi '(^|[^[:alnum:]_])provisioner([^[:alnum:]_]|$)' && echo 1)
has_exec=$(printf '%s' "$content" | grep -Eqi '(local|remote)-exec' && echo 1)
has_tf_apply=$(printf '%s' "$content" | grep -Eqi '(^|[^[:alnum:]_./-])terraform[[:space:]]+(apply|destroy)([[:space:]]|$|")' && echo 1)

if [ "$has_provisioner" = "1" ] && [ "$has_exec" = "1" ] && [ "$has_tf_apply" = "1" ]; then
  deny "provisioner(local-exec/remote-exec) 内での terraform apply/destroy は禁止です（.tf へのバックドア防止）。${file_path} から該当の provisioner を削除してください。apply/destroy はユーザーが手動で実施します。"
fi

exit 0
