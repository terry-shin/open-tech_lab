#!/usr/bin/env bash
# PreToolUse(Bash) hook: terraform の AWS 認証コマンド実行前に、ログイン中の AWS profile を検査する。
# - SSO 未認証          -> deny（aws sso login を促す）
# - administrator 相当  -> deny（read-only profile への切替を促す）
# - それ以外（read-only 等） -> 許可（無出力で exit 0）
# macOS の bash 3.2 でも動くよう、空配列展開を避けラッパ関数で profile 引数を分岐する。
# set -e/-u は使わず、AWS/grep の失敗は明示的に握る。

input=$(cat)
cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // ""' 2>/dev/null)

# 認証が必要な terraform サブコマンドのみ対象（apply/destroy は別 hook で deny 済みのため対象外）
auth_re='(^|[^[:alnum:]_./-])terraform[[:space:]]+(init|plan|import|refresh|state|console|output|show|providers|taint|untaint|force-unlock)([[:space:]]|$)'
if ! printf '%s' "$cmd" | grep -Eq "$auth_re"; then
  exit 0
fi

# deny JSON を出力して終了（reason は jq -Rs で安全に文字列化）
deny() {
  reason_json=$(printf '%s' "$1" | jq -Rs .)
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":%s}}' "$reason_json"
  exit 0
}

# profile 解決: コマンド内 AWS_PROFILE=... を優先 -> 環境変数 -> default(空)
prof=$(printf '%s' "$cmd" | grep -oE 'AWS_PROFILE=[^[:space:];&|]+' | head -n1 | cut -d= -f2- | tr -d '"'"'"'' )
if [ -z "$prof" ]; then
  prof="$AWS_PROFILE"
fi

# profile 有無で --profile を分岐する aws ラッパ
awsx() {
  if [ -n "$prof" ]; then
    aws --profile "$prof" "$@"
  else
    aws "$@"
  fi
}

prof_label="${prof:-default}"

# (1) SSO / 認証チェック
arn=$(awsx sts get-caller-identity --query Arn --output text 2>/dev/null)
if [ -z "$arn" ] || [ "$arn" = "None" ]; then
  deny "AWS 未認証です（profile: ${prof_label}）。プロンプトで '! aws sso login --profile ${prof_label}' を実行して再ログインしてから、terraform を再実行してください。"
fi

# (2) administrator 相当チェック（手法A: AdministratorAccess の有無）
case "$arn" in
  *:assumed-role/*)
    role=$(printf '%s' "$arn" | sed -E 's#.*assumed-role/([^/]+)/.*#\1#')
    admin=$(awsx iam list-attached-role-policies --role-name "$role" \
      --query "AttachedPolicies[?PolicyName=='AdministratorAccess'].PolicyName" \
      --output text 2>/dev/null)
    if [ "$admin" = "AdministratorAccess" ]; then
      deny "administrator 相当の権限を持つ profile（${prof_label} / role: ${role}）で terraform の AWS 認証コマンドを実行しようとしています。誤操作防止のため read-only profile へ切替えてください（例: export AWS_PROFILE=<read_only> 後、必要なら ! aws sso login）。"
    fi
    ;;
esac

# 許可
exit 0
