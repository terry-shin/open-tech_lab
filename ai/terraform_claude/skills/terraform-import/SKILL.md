---
name: terraform-import
description: base-terraform で既存AWSリソース（EC2等）をTerraform管理にimportする手順。前提として AWS SSO ログイン（aws sso login）が必須。AWS CLI（read-only）で実態を取得し、既存雛形（baseec/ec2/development の track ブロック）に倣ってコードを追加、import block 方式で `terraform plan` まで検証する（apply はユーザーが実施）。「importしたい」「Terraform管理に取り込みたい」「terraform import」といった依頼時に使用する。
---

# Terraform 既存リソース import 手順

このリポジトリ（base-terraform）で、AWS上に手動作成された既存リソースを Terraform 管理へ取り込むための標準手順。EC2 を主対象とし、付随する ENI / EIP / EBS も扱う。

## 0. 前提・ガードレール（必ず守る）

- **事前に AWS SSO ログインが必須。** この手順の profile（例 `baseecdev_read_only`）は AWS IAM Identity Center（SSO）ベースのため、AWS CLI / Terraform を実行する前に対象 profile で `aws sso login` 済みであること（未認証だと token 期限切れで全コマンドが失敗する）。`aws sso login` はブラウザを開く**対話コマンドのため AI は実行せず、ユーザーに依頼する**（プロンプトで `! aws sso login --profile <profile>` を実行してもらう）。実行直前の確認は Step 1 のプリフライト参照。
- **`terraform apply` / `terraform destroy` は絶対に実行しない。** このスキルのゴールは **`terraform plan` の差分確認まで**。state への取り込み（apply）以降はユーザーが手動で行う。
  - `.claude/settings.json`（`permissions.deny` + `PreToolUse` hook）と `.claude/CLAUDE.md` でも禁止済み。
- 調査・plan は **read-only profile**（例: `baseecdev_read_only`）で行う。各環境の profile は対象ディレクトリの `.envrc`（`AWS_PROFILE=...`）を参照。
- **import に admin 権限は不要。** ログイン中の profile が administrator 相当の場合は、**誤操作防止のため作業を中止する**（Step 1 プリフライトの権限レベルチェック）。
- read-only profile は state lock（`s3:PutObject`）ができないため、`terraform plan` には **`-lock=false`** を付ける。
- 作業前に**作業ブランチを作成**（default ブランチを pull してから）。`master`/`main`/`development` へ直接変更しない。
- **確認なしに commit / push / ドキュメント変更をしない。** 秘密情報（鍵・token）はコードに直書きしない。

## 1. 対象リソースの実態取得（AWS CLI / read-only）

対象の Name タグ（例 `ec-dev-nginx-static-al2023`）から実態を取得する。`export AWS_PROFILE=<read_only profile>` を先頭で設定。

**プリフライト（SSO 認証チェック）**: AWS CLI を叩く前に、SSO セッションが有効か確認する。

```bash
export AWS_PROFILE=<read_only profile>
aws sts get-caller-identity --query Arn --output text \
  && echo "SSO OK" \
  || echo "未認証: ユーザーに 'aws sso login --profile <profile>' を依頼する"
```

`get-caller-identity` が失敗した場合（`Token has expired` / `not authorized` 等）は SSO 未ログイン。**ユーザーにプロンプトで `! aws sso login --profile <profile>` の実行を依頼**し、成功を確認してから以降を再開する（対話ログインのため AI は実行しない）。

**プリフライト（権限レベルチェック）**: import の調査・plan は read-only 権限で十分。ログイン中の profile が **administrator 相当**だと、誤って破壊的操作（apply/destroy 等）が可能な状態のまま作業することになるため、検出したら続行可否をユーザーに確認する。手法A（アタッチ済みマネージドポリシーの確認）で判定する。

```bash
# assumed-role ARN からロール名を取り出し、AdministratorAccess の有無を確認
ROLE=$(aws sts get-caller-identity --query Arn --output text | sed -E 's#.*assumed-role/([^/]+)/.*#\1#')
aws iam list-attached-role-policies --role-name "$ROLE" \
  --query "AttachedPolicies[?PolicyName=='AdministratorAccess'].PolicyName" --output text
# 参考: 付与ポリシー全体を見る場合
# aws iam list-attached-role-policies --role-name "$ROLE" --query 'AttachedPolicies[].PolicyName' --output json
```

判定と分岐:
- **出力が空** → administrator 相当ではない（read-only 等）。そのまま続行する。
- **`AdministratorAccess` が返る**（または運用上 admin 相当と判明している profile）→ **AskUserQuestion で続行可否をユーザーに確認する**。
  - 例:「administrator 相当の権限を持つ profile（`<profile>`）でログイン中です。import の調査・plan は read-only 権限で十分で、admin のままだと誤操作のリスクがあります。このまま続行しますか？」
  - 「続行しない」を選んだ場合は、read-only profile への切替（`export AWS_PROFILE=<read_only>` ＋必要なら `! aws sso login --profile <read_only>`）を案内し、再ログイン後に再開する。
- **`list-attached-role-policies` が AccessDenied**（IAM 参照権限が無い）→ admin である可能性は低いが断定はできない。その旨を伝え、判断をユーザーに委ねた上で続行する。

```bash
# 基本情報
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=<対象Nameタグ>" \
  --query 'Reservations[].Instances[].{InstanceId:InstanceId,State:State.Name,Type:InstanceType,AMI:ImageId,Subnet:SubnetId,IAM:IamInstanceProfile.Arn,Key:KeyName,ENI:NetworkInterfaces[].NetworkInterfaceId,SG:SecurityGroups[].GroupId,PublicIp:NetworkInterfaces[].Association.PublicIp}' \
  --region ap-northeast-1 --output json
```

続けて以下で詳細を取得する（InstanceId / ENI を埋めて実行）:

- `aws ec2 describe-addresses --filters "Name=instance-id,Values=<id>"` … **EIP の実在確認**。空なら public IP は auto-assign であり `aws_eip` / `aws_eip_association` は**作らない**。結果があれば AllocationId / AssociationId を控える。
- `aws ec2 describe-network-interfaces --network-interface-ids <eni>` … ENI の subnet / SG / private IP。
- `aws ec2 describe-volumes --filters "Name=attachment.instance-id,Values=<id>"` … root volume の size / type / iops / throughput / encrypted。
- `aws ec2 describe-security-groups --group-ids <sg...>` … SG 名（既存 data に無いものを洗い出す）。
- `aws ec2 describe-images --image-ids <ami>` … AMI 名 / CreationDate（→ リソース名のバージョン日付に使う）。

**命名規則**
- Name タグ: `ec-{env}-{role}-al2023`（例 `ec-dev-nginx-static-al2023`）。
- Terraform リソース名: `{role}_v{AMI作成日YYYYMMDD}`（例 AMI 作成日 2024-11-20 → `nginx_static_v20241120`）。アンダースコア区切り。

## 2. 配置先ディレクトリと雛形の特定

| 環境 | ディレクトリ | state キー（bucket: `ec-dev-terraform-tfstate`） |
|---|---|---|
| development | `baseec/ec2/development/` | `baseecdev/ec2-instance.tfstate` |
| staging / production | 各対応ディレクトリ直下 | 各 `environment.tf` の backend を参照 |

- **雛形**: `baseec/ec2/development/common.tf` の `track` ブロック（EC2 + ENI、必要なら EIP のセット、`lifecycle { ignore_changes = all }`）。`mail-batch` も同型。
- **既存 locals/data の確認先**: `variables.tf`（AMI ID・IAM instance profile・subnet・security group の `data`/`local`）。流用できるものは再定義しない。

## 3. variables.tf に不足定義を追加

実態取得で判明し、既存 `variables.tf` に無いものだけを既存の書式に倣って追加する。

- AMI 未登録: `locals` の ami セクションに `ami_id_al2023_v<日付> = "<ami-id>"`。
- 未定義 SG: `data "aws_security_group" "<name>" { id = "<sg-id>" }` と `local.<name>_sg_id = data...id`。
- 未定義 subnet: 同様に `data "aws_subnet"` + `local`。

## 4. `<role>.tf` を新規作成

`track` 雛形を流用し、実態に合わせて作る。EIP は **Step1 で実在を確認できた場合のみ**定義する。

```hcl
# <role>
## EC2
resource "aws_instance" "<role>_v<日付>" {
  ami                  = local.ami_id_al2023_v<日付>
  instance_type        = "<type>"
  iam_instance_profile = local.<...>_iam_role
  user_data            = templatefile("templates/user_data.sh", { HOSTNAME = "ec-<env>-<role>-al2023" })
  key_name             = "<key>"

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
    Name              = "ec-<env>-<role>-al2023"
    IdentityFile      = local.identity_file_path
    User              = "ec2-user"
    DeployEnvironment = "<env>"
    DeployType        = "<role>"
  }

  lifecycle {
    # 変更はすべて無視
    ignore_changes = all
  }
}

## network interface
resource "aws_network_interface" "<role>_v<日付>" {
  subnet_id       = local.<subnet>_id
  security_groups = [ /* 実態のSGを local 参照で列挙 */ ]

  tags = {
    Name = "ec-<env>-<role>-al2023"
  }
}

## import（取り込み後に削除する）
import {
  to = aws_instance.<role>_v<日付>
  id = "<instance-id>"
}
import {
  to = aws_network_interface.<role>_v<日付>
  id = "<eni-id>"
}
```

- EIP が実在する場合のみ `aws_eip`（`lifecycle { ignore_changes = [tags] }`）と `aws_eip_association` を追加し、それぞれ `import` ブロック（id は EIP=AllocationId、association=AssociationId）も足す。

## 5. 検証（plan まで＝ゴール）

対象ディレクトリで read-only profile を設定して実行:

```bash
terraform fmt <role>.tf variables.tf
terraform validate
terraform init -input=false
terraform plan -input=false -no-color -lock=false
```

**確認基準**
- `Plan: N to import, 0 to add, 0 to destroy.`（import 対象が想定の instance / ENI(/EIP) であること）。
- 置換（`-/+`）や、import ではない新規作成（add）が**無い**こと。
- `aws_instance` は `ignore_changes = all` のため **import のみで変更なし**。
- `aws_network_interface` は ENI への Name/default タグ追加など軽微な in-place update のみ（想定内）。subnet/SG に差分が出ないこと。

→ plan 結果をユーザーに報告してスキルは完了。

## 6. 以降の手順（ユーザーが実施・スキル範囲外）

1. 書込権限のある profile で `terraform apply` → state 取り込み。
2. `terraform plan` が **No changes** になることを確認。
3. `import { ... }` ブロックを `<role>.tf` から削除し、再度 `terraform plan` が No changes であることを確認（リポジトリ慣習: import block 追加→取込→削除）。
4. commit（例: `Add: <env>環境の<role> EC2を既存リソースからimport`）。

---

## 慣習リファレンス（早見表）

| 項目 | 値 |
|---|---|
| Name タグ | `ec-{env}-{role}-al2023` |
| リソース名 | `{role}_v{AMI作成日YYYYMMDD}` |
| lifecycle | instance/ENI 既存取込は `ignore_changes = all`、EIP は `[tags]` |
| ネットワーク | ENI を `aws_network_interface` で分離し `primary_network_interface` で参照 |
| EIP | 実在時のみ定義（auto-assign public IP は対象外） |
| import 方式 | `import {}` ブロック → apply → ブロック削除 |
| 認証 | 実行前に `aws sso login --profile <profile>` 必須（SSO=IAM Identity Center）。対話ログインは AI 不可・ユーザー実行 |
| profile | 調査/plan は read-only（`.envrc` 参照）、apply はユーザーが書込 profile |
| plan | `-lock=false`（read-only は lock 不可） |

## 実行チェックリスト

- [ ] AWS SSO ログイン済み（`aws sts get-caller-identity` で確認。未認証ならユーザーに `aws sso login` を依頼）
- [ ] ログイン profile の権限レベルを確認（手法A）。admin 相当なら続行可否をユーザーに確認した
- [ ] 作業ブランチを作成した（default を pull 後）
- [ ] AWS CLI（read-only）で instance / ENI / EIP / volume / SG / AMI の実態を取得した
- [ ] 配置ディレクトリと `track` 雛形・既存 locals を確認した
- [ ] `variables.tf` に不足する AMI / SG / subnet を追加した
- [ ] `<role>.tf` を作成（EIP 有無を実態一致、`ignore_changes=all`、import block）
- [ ] `fmt` / `validate` / `init` / `plan -lock=false` を実行した
- [ ] plan が `to import` 中心で add/destroy/置換なしを確認し、ユーザーに報告した
- [ ] **apply / destroy は実行していない**
