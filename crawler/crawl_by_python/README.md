# crawl_by_python

## ■概要
Pythonによるクローラー作成検証用

### 主な初期導入ミドル
- python3.8
- jupyterlab
  - selenium

#### [ディレクトリ構成]
  ```
  crawl_by_python
  │
  ├── notebooks  # juypterlabのworkディレクトリ
  │   ├── output      # スクショなどのoutput用ディレクトリ
  │   └── crawler.ipynb   #クローラーサンプル
  ├── work    # 作業ディレクトリ。現時点では未使用
  │       
  └── READMEやローカル環境用Dockerファイル

  ```

#### 個別設定
マウントしたいディレクトリに応じて、docker-compose.yamlを書き換え

```    
volumes:
      - ./work:/usr/local/src/work #作業用ディレクトリ
      - ./notebooks:/usr/local/src/notebooks #jupyterlab ホームホームディレクトリ
```

## ■ローカル環境 セッティング

#### ローカルでの前準備
- このディレクトリをローカルに配置
- Dockerを使えるようにしておく

- ローカルに配置した「crawl_by_python」に移動

#### build実行
- 下記コマンドを実行
  - 少し時間かかります
  - ※初回のみ
```
$ docker-compose build --no-cache
```

#### コンテナ起動・停止
- 正常であればローカル環境が起動する
```
$ docker-compose up
```
- 以下のようなログが出るので、「http://127.0.0.1:8080/」のURLにブラウザでアクセス
  - jupyterlabの画面にアクセスできるので、そこでコーディング&動作検証

- 停止の場合は「Ctl+C」
  - 環境壊れた場合は、以下を実施
```
$ docker-compose down
```

#### コンテナにssh
- アプリの実行ログを見る場合等に実行
  - 下記コマンドを実行
```
$ docker-compose exec sandbox bash
```
