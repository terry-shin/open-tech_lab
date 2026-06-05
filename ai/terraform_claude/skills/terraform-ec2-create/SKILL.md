---
name: terraform-ec2-create
description: base-terraform で既存EC2（別環境のもの）を参照に、別環境へ同種のEC2を新規作成する手順。前提として AWS SSO ログイン（aws sso login）が必須。参照元の `.tf` からスペックを抽出し、配置先環境の既存EC2（`web.tf` 等）の流儀（IAM/SG/subnet/lifecycle/tags の参照書式）に合わせて新規リソースを定義、import block なしで `terraform plan`（= N to add）まで検証する（apply はユーザーが実施）。「prdの〇〇を参考にstg/devに同じEC2を作りたい」「別環境に同種のEC2を新規作成」といった依頼時に使用する。既存リソースの取り込みは terraform-import スキルを使う。
---

# Terraform EC2 新規作成（既存EC2を参照）手順

このリポジトリ（base-terraform）で、ある環境の既存EC2（例 `ec-prd-nginx-static-al2023`）を参照に、別環境（staging / development）へ**同種のEC2を新規プロビジョニング**するための標準手順。EC2 + ENI を主対象とする。

**terraform-import との違い**:
- import block を**付けない**（state へ取り込むのではなく、実インスタンスを新規作成する）。
- plan の期待結果は `to import` ではなく **`N to add`**。
- 参照元のスペックを使いつつ、**配置先環境の既存EC2の流儀**（IAM/SG/subnet/lifecycle/tags の参照先と書式）に合わせる ＝ 環境差分の吸収が核。
- 既存リソースを Terraform 管理へ取り込む場合は terraform-import スキルを使う。

## 0. 前提・ガードレール（必ず守る）

- **事前に AWS SSO ログインが必須。** 配置先の profile（例 `baseecstg_read_only_sre`）は AWS IAM Identity Center（SSO）ベースのため、AWS CLI / Terraform 実行前に対象 profile で `aws sso login` 済みであること。`aws sso login` はブラウザを開く**対話コマンドのため AI は実行せず、ユーザーに依頼する**（プロンプトで `! aws sso login --profile <profile>` を実行してもらう）。
- **`terraform apply` / `terraform destroy` は絶対に実行しない。** このスキルのゴールは **`terraform plan` の差分確認まで**。apply 以降はユーザーが手動で行う（`.claude/settings.json` の `permissions.deny` + `PreToolUse` hook、`.claude/CLAUDE.md` でも禁止済み）。
- 調査・plan は **read-only profile** で行う。各環境の profile は対象ディレクトリの `.envrc`（`AWS_PROFILE=...`）を参照。**ただし `.envrc` の profile 名が実在しないことがある**（Step 1 で `aws configure list-profiles` により実在確認する）。
- **作業前に作業ブランチを作成**（default ブランチを pull してから）。`master`/`main`/`development` へ直接変更しない。
- **確認なしに commit / push / ドキュメント変更をしない。** 秘密情報（鍵・token）はコードに直書きしない。

## 1. 認証・profile のプリフライト

配置先環境の `.envrc` を確認して profile を把握する。`.envrc` の記載が実在するとは限らないため、必ず実在確認する。

```bash
# .envrc 記載の profile が実在するか確認。無ければ近い read-only profile を探す
aws configure list-profiles | grep -iE "<env略称>|read"
# 例: staging なら baseecstg_read_only_sre が read-only 相当
```

**SSO 認証チェック**（read-only profile を埋めて実行）:

```bash
AWS_PROFILE=<read_only profile> aws sts get-caller-identity --query Arn --output text \
  && echo "SSO OK" \
  || echo "未認証: ユーザーに 'aws sso login --profile <profile>' を依頼する"
```

失敗時（`Token has expired` 等）は **ユーザーにプロンプトで `! aws sso login --profile <profile>` を依頼**し、成功を確認してから再開（対話ログインのため AI は実行しない）。

**権限レベルチェック**: 調査・plan は read-only で十分。ログイン中 profile が **administrator 相当**だと誤操作リスクがあるため、検出したら続行可否をユーザーに確認する（assumed-role 名 → `AdministratorAccess` の有無）。

```bash
ROLE=$(AWS_PROFILE=<profile> aws sts get-caller-identity --query Arn --output text | sed -E 's#.*assumed-role/([^/]+)/.*#\1#')
AWS_PROFILE=<profile> aws iam list-attached-role-policies --role-name "$ROLE" \
  --query "AttachedPolicies[?PolicyName=='AdministratorAccess'].PolicyName" --output text
```

- 出力が空 → read-only 等。続行。
- `AdministratorAccess` が返る → AskUserQuestion で続行可否を確認。read-only への切替を案内。
- `AccessDenied` → admin の可能性は低いが断定不可。その旨を伝え判断を委ねて続行。

## 2. 参照元リソースのスペック抽出

参照元の `.tf`（例 `baseec/ec2/production/nginx-static.tf`）と、その `variables.tf` を読み、以下を抽出する。**実態は参照元の Terraform コードから取得できるため、AWS CLI での実機確認は必須ではない**（参照元が信頼できる前提）。

抽出項目: `ami` / `instance_type` / `iam_instance_profile` / `key_name` / `user_data`（HOSTNAME）/ `root_block_device`（size/type/iops/throughput/encrypted）/ `tags` / `lifecycle.ignore_changes` / ENI の `subnet_id` / `security_groups`。

## 3. 配置先環境の流儀調査（最重要）

配置先環境の**既存EC2**（例 staging の `baseec/ec2/staging/web.tf`）と `variables.tf` を読み、以下を確定する。

- **参照書式**: IAM/SG/subnet を `local.*` 経由でどう参照しているか（例 `local.web_iam_role` / `local.ec_web_sg_id` / `local.sn_stg_pri_1c_id`）。
- **既存 locals/data**: `variables.tf` に流用できる AMI・IAM instance profile・SG・subnet があるか。流用できるものは再定義しない。
- **不足リソースの洗い出し**: 参照元が使うリソースが配置先に**無い**ケースを特定する（実例）。
  - IAM instance profile: ロールはあっても instance profile 未作成のことがある。
  - security group: `tenable-scan-target-sg` 等が配置先環境に存在しないことがある。
- **書式の差分**: 配置先既存EC2の `tags`（例 `Name/IdentityFile/User` のみ）や `lifecycle.ignore_changes`（例 `[tags, instance_type]`）の慣習に合わせる。参照元（prd）と異なることがある。

## 4. 決定点の確認（AskUserQuestion）

参照元スペックと配置先の流儀に差がある項目は、**勝手に決めず AskUserQuestion で確認**する。典型的な決定点:

- **AMI**: 参照元と同一バージョンを使うか、配置先の最新 AMI（既存 locals）に揃えるか。
- **IAM instance profile**: 参照元同等（不足なら新規作成）か、配置先の既存（例 `web` の profile）流用か。
- **security group**: 参照元同等（不足分は新規作成）か、配置先の既存SG流用か。
- **instance_type / root volume**: 参照元同等か、配置先の同役割EC2に揃えるか。

新規作成が必要な IAM/SG が出た場合は、その追加（`iam_system/<env>`・`security_group/<env>`）も計画に含めるか確認する。

## 5. リソース命名

- Name タグ / hostname: 参照元の `ec-{srcenv}-{role}-al2023` の env 部分を置換（例 `ec-prd-...` → `ec-stg-...`）。
- Terraform リソース名: `{role}_v{採用AMIの日付YYYYMMDD}`（例 採用 AMI が v20260527 → `nginx_static_v20260527`）。配置先既存EC2のサフィックス慣習に合わせる。

## 6. `<role>.tf` を新規作成

配置先の既存EC2パターンに準拠。**import block は付けない**。

```hcl
# <role>
## instance
resource "aws_instance" "<role>_v<日付>" {
  ami                  = local.ami_id_al2023_v<日付>
  instance_type        = "<type>"
  iam_instance_profile = local.<...>_iam_role
  user_data            = templatefile("templates/user_data.sh", { HOSTNAME = "ec-<env>-<role>-al2023" })
  key_name             = "base-ops"

  primary_network_interface {
    network_interface_id = aws_network_interface.<role>_v<日付>.id
  }

  root_block_device {
    delete_on_termination = true
    encrypted             = <bool>
    iops                  = <iops>
    kms_key_id            = null
    tags                  = { "Name" = "ec-<env>-<role>-al2023" }
    throughput            = <throughput>
    volume_size           = <size>
    volume_type           = "<type>"
  }

  tags = {
    # 配置先既存EC2の tags 慣習に合わせる（prd の DeployEnvironment/DeployType は付けない環境もある）
    Name         = "ec-<env>-<role>-al2023"
    IdentityFile = local.identity_file_path
    User         = "ec2-user"
  }

  lifecycle {
    # 配置先既存EC2の慣習に合わせる（例: [tags, instance_type]）
    ignore_changes = [tags, instance_type]
  }
}

## network interface
resource "aws_network_interface" "<role>_v<日付>" {
  subnet_id       = local.<subnet>_id
  security_groups = [local.<sg>_id]

  tags = {
    Name = "ec-<env>-<role>-al2023"
  }

  lifecycle {
    ignore_changes = [tags]
  }
}
```

Step 4 で IAM/SG/subnet の新規追加を決めた場合は、`variables.tf`（data/local）や `iam_system/<env>`・`security_group/<env>` に既存書式で追加する。

## 7. 検証（plan まで＝ゴール）

対象ディレクトリ（`baseec/ec2/<env>/` 直下）で read-only profile を設定して実行:

```bash
AWS_PROFILE=<read_only profile> terraform fmt
AWS_PROFILE=<read_only profile> terraform init -input=false   # 未初期化時
AWS_PROFILE=<read_only profile> terraform validate
AWS_PROFILE=<read_only profile> terraform plan -input=false -no-color
```

> read-only で state lock できずエラーになる場合は `terraform plan` に `-lock=false` を付ける。

**確認基準**
- `Plan: N to add, 0 to change, 0 to destroy.`（追加が想定の instance / ENI であること）。
- import 関連の警告が**無い**こと（新規作成のため）。
- 参照する SG / subnet ID が想定どおりであること（plan 出力で確認）。

→ plan 結果をユーザーに報告してスキルは完了。

## 8. 以降の手順（ユーザーが実施・スキル範囲外）

1. 書込権限のある profile で `terraform apply` → 実インスタンス作成。
2. 必要なら、採番された instance ID を `ops_tools/ec2_auto_recovery/<env>/variables.tf` の `instance_ids` に追記（auto-recovery 対象に登録）。
3. commit（例: `Add: <env>環境の<role> EC2を新規作成`）。

---

## 慣習リファレンス（早見表）

| 項目 | 値 |
|---|---|
| Name タグ / hostname | `ec-{env}-{role}-al2023`（参照元の env を置換） |
| リソース名 | `{role}_v{採用AMI作成日YYYYMMDD}` |
| import block | **付けない**（新規作成） |
| plan 期待値 | `N to add, 0 to change, 0 to destroy`（import 警告なし） |
| tags / lifecycle | **配置先環境の既存EC2に合わせる**（参照元 prd と異なることがある） |
| IAM/SG/subnet | 既存 locals/data を流用。不足分は決定点として確認 |
| 認証 | 実行前に `aws sso login --profile <profile>` 必須。対話ログインは AI 不可・ユーザー実行 |
| profile | `.envrc` 記載が実在しないことあり → `aws configure list-profiles` で実在確認 |

## 実行チェックリスト

- [ ] 配置先 `.envrc` の profile を確認し、`aws configure list-profiles` で実在を確認した
- [ ] AWS SSO ログイン済み（`aws sts get-caller-identity` で確認。未認証ならユーザーに依頼）
- [ ] ログイン profile の権限レベルを確認（admin 相当なら続行可否を確認）
- [ ] 作業ブランチを作成した（default を pull 後）
- [ ] 参照元 `.tf` / `variables.tf` からスペックを抽出した
- [ ] 配置先の既存EC2（`web.tf` 等）の流儀・既存 locals・不足リソースを調査した
- [ ] 差分のある項目（AMI/IAM/SG/type/volume）を AskUserQuestion で確定した
- [ ] `<role>.tf` を作成（import block なし、配置先の tags/lifecycle 慣習に準拠）
- [ ] 必要なら不足 IAM/SG/subnet を追加した
- [ ] `fmt` / `init` / `validate` / `plan` を実行した
- [ ] plan が `to add` 中心で change/destroy/import 警告なしを確認し、ユーザーに報告した
- [ ] **apply / destroy は実行していない**
