# python開発用

## 主な初期導入ミドル
- python3.8
- juypterlab
  - selenium

### 個別設定
マウントしたいディレクトリに応じて、docker-compose.yamlを書き換え

```    
volumes:
      - ./work:/usr/local/src/work #作業用ディレクトリ
      - ./notebooks:/usr/local/src/notebooks #jupyterlab ホームホームディレクトリ 
```

## sandbox 利用方法

- いずれもsandbox直下実行


コンテナbuild

```
$ docker-compose build --no-cache
```

コンテナ起動

```
$ docker-compose up
```

コンテナに入る

```
$ docker-compose exec sandbox bash
```

コンテナ停止

```
$ docker-compose down
```
