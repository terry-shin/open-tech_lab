# nuxt & firebase検証用

## 環境
- vscode

## ■ディレクトリ構成
```
nuxt_sandbox
│
├── .devcontainer  # vscode用localコンテナ設定Dir
│
├── [nuxt プロジェクトディレクトリ]
│   │
│   └── nuxtファイル一式
│
├── sample
│   │
│   └── サンプルファイルディレクトリ # ログインとか実装例を格納予定
│
├── doc                   # ドキュメントディレクトリ
│
│
└── READMEなど
```


## ■検証用コンテナ
- vscodeにて「Open Folder in Container」で当ディレクトリ を指定



----
## ■nuxt
- [NuxtJSドキュメント](https://nuxtjs.org/ja/docs/get-started/installation)
### 【前提知識】
- SPA(シングルページアプリケーション)：最もシンプル
- SSR(サーバーサイドレンダリング)：サーバー側でHTMLを生成し返却する
    - [参考](https://zenn.dev/kokota/articles/cd2aa18365aa91)
- SSG(静的サイトジェネレーター)：静的ファイルのみのサイト

### 【プロジェクト作成】
- プロジェクト作成コマンド
  - 実行すると、プロジェクト名のディレクトリ が生成される
    - うまくいかない場合は新しいディレクトリを作成して、その配下で。
  - [参考](https://www.willstyle.co.jp/blog/3545/)
    ```
    npx create-nuxt-app [プロジェクト名]
    ```
  - 設定例
  
    ![サイト追加](/sandbox/sandbox_nuxt/doc/image/プロジェクト作成.png)
    - Nuxt.js modules
      - Axiosは非同期通信のモジュール
      - PWAはProgressive Web Appに対応させるためのモジュール、ContentはMarkdownを使えたりGitベースでのヘッドレスCMSを構築する際に非常に便利なモジュール

### 【主要コマンド】
**※プロジェクトディレクトリに移動して実行※**
- ローカル開発環境 起動
  - ファイル更新の度に反映される
  ```
  npm run dev
  ```
- プロダクションモード起動
  - **build または generate**を前もって実行
  ```
  npm run start
  ```

- 更新内容反映
  - SPAはどちらでも問題ない？
  - build
    - JS と CSS をプロダクション向けにミニファイする
    - .nuxt配下に出力
    ```
    npm run build
    ```
  - generate
    - seiteki 
    - 静的サイトへのデプロイのための静的ファイル生成
    - dist配下に出力
      ```
      npm run generate
      ```

### 【テストページ】
- アクセス
  - http://localhost:3000
  ![サイト追加](/sandbox/sandbox_nuxt/doc/image/サンプルページ.png)

- nuxt.config.jsにserver設定を記載しないと、見れない可能性あり
  - [参考](https://nuxtjs.org/ja/docs/configuration-glossary/configuration-server/)
  ```
    server: {
      port: 8000, // デフォルト: 3000を変えたい場合
      host: '0.0.0.0', // デフォルト: localhost,
      timing: false
    }
  ```
- **pages/index.vue**を更新してみる
  - 反映されたら成功 

- Vuetifyインストール済みなので、利用可
    - [Vuetifyについて](https://prograshi.com/language/vue-js/how-to-use-vuetify/) 

----




## ■Firebase
### 【Firebasecliの許可】
- ターミナルから下記を実行
```
firebase login
```
※9005 ポートをあけてないと認証は通らない？

### 【セッティング】
- Firebaseの「Hosting」から、サイトを追加


### 【初期処理】
- nuxtのPJディレクトリに移動して実行
```
firebase init
```


- firebase.json編集
```
{
  "hosting": {
    "target": "[任意のサイト名]",
    "public": "[アップロードするディレクトリ]",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ]
  }
}
```

- 【アプリ設定追加】
```
firebase target:apply hosting [任意のサイト名] [Firebase上でのサイト]
```

-  デプロイ
    - SPAの場合
        ```
        npm run generate
        ```
    - デプロイコマンド
        - コマンド実行で、アップディレクトリ一式がGCPにアップロードされる
        ```
        firebase deploy --only hosting:[任意のサイト名]
        ```

