## 技術検証用リポジトリ
### ai
主にClaude系の設定とか
- common_claude
  - 共通で使う設定
- terraform_claude
  - terraformで使う設定
- claude-code-template
  - いろんなエージェントとか実業務を想定したセット

### api-blueprint
APIのIF仕様書作成用

### crawler
クローラー一式
- crawl_by_pytyon
  - putyon サンプルクローラー
- crawl_by_node
  - Nodejs サンプルクローラー

### gcp
#### gcf
CloudFunctions Python用サンプル関数
- pub_test
  - Pub/SubのPublisher側 関数
- sub_test
  - Pub/SubのSubscriber側 関数
- sample_function
  - ClousStrageトリガーで動くスクレイピング 関数

### name-search
法人名識別スクリプト

### sandbox
技術検証用ローカル環境 構築
- sandbox_pytyon
  - python検証ローカル環境一式
    - jypterlab
- sandbox_node
  - node検証用ローカル環境一式

