# crawl_by_node

## ■概要
Nodejsによるクローラー作成検証用

### 主な初期導入ミドル
- node12
- puppeteer

#### [ディレクトリ構成]
```
crawl_by_node
│
├── output  # スクショなどのoutput用ディレクトリ
├── work    # 作業ディレクトリ。基本はこの配下ファイルに対して手を入れる
│   ├── config      #設定ファイルディレクトリ
│   ├── app.js      #クローラーサンプル
│   ├── incude      #関数ディレクトリ
│   └── sample.js   #テスト用ファイル
│       
└── READMEやローカル環境用Dockerファイル

```

## ■ローカル環境 セッティング

#### ローカルでの前準備
- このディレクトリをローカルに配置
- Dockerを使えるようにしておく

- ローカルに配置した「crawl_by_node」に移動

#### build実行
- 下記コマンドを実行
  - 少し時間かかります
  - ※初回のみ
```
$ docker-compose build --no-cache
```

#### コンテナ起動・停止
- 正常であればローカル環境が起動する
  - バックグラウンド処理の場合は「-d」をつける
```
$ docker-compose up
```

- 停止の場合は「Ctl+C」
  - 環境壊れた場合は、以下を実施
```
$ docker-compose down
```

#### コンテナにssh
- アプリの実行ログを見る場合等に実行
  - 下記コマンドを実行
```
$ docker-compose exec nodejs bash
```

- 初期ディレクトリ
>/usr/local/src/app

- 直下の*「work」*ディレクトリに、ローカルの*「crawl_by_mode/work」*がマウントされている

## ■クローラーサンプルについて
- Nodejsで作成した簡易クローラー
- 現在のサポートツールのクローラーで取得している情報をとる
  - [参照](https://docs.google.com/spreadsheets/d/1pjA3oc7jsHamx6QjcpZZ0r7_eB6Wb8pOsXqsJtg9mxI/edit#gid=0)

#### 実行
- ブラウザで以下のurlにアクセス
  - [キーワード]を、対象としたい文字列（例：ビール、ワイン）にする。

```
http://localhost:8080/crawl?k=[キーワード]
```

- 正常終了した場合、以下の「END:YYYYMMDDHH24MISS」文字列が表示される

```
例
END:20201202203953
```

- クローリングして取得できた情報は、コンテナにsshして、以下のログから確認できる
>/usr/local/src/app/logs/app.log
