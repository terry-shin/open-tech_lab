# custom_jcl_toolsについて

- 国税庁の企業データから、カスタムJCL(Japanese Company Lexicon)を生成する

## 構成

[ディレクトリ構成]
```
custom_jcl_tools
│
├── work  # python
│   ├── custom      #独自Class格納dir
│   ├── data        #inputファイル格納dir
│   ├── custom_jcl  #tisのdic生成処理をカスタマイズしたものを格納
│   └── work直下     #各種pythonファイル      
└── README.mdやローカル検証用Dockerファイル

```

## 利用方法

※localのpython環境手順は省略

### カスタムJCL(独自企業名辞書)の生成
作業dirに移動
```
$ cd custom_jcl/
```

zipファイルの格納
- 国税庁のサイトから取得
  - https://www.houjin-bangou.nta.go.jp/download/zenken/
  - 「CSV形式・Unicode」を使用

```
# 配置場所
custom_jcl_tools/work/custom_jcl/data/hojin
```
※ tools/downloader.py を使えばDLできるかも？（未実施）

downloadシェル実行
- zipを入れていれば、ここで解凍される
  - zipファイルと必要ディレクトリ生成しているだけなので、頻繁には実行しない？
```
$ ./scripts/download.sh
```

エイリアス生成シェル実行

```
$ ./scripts/custom_generate_alias.sh


# 以下に生成したエイリアスファイルが出力される
data/hojin/output
data/dictionaries/output
```

カスタムJCL形式に加工
```
 $ python ./tools/custom_jcl_save.py

 # 以下にmecabのcsvファイルが出力される
 data/dictionaries/output/cutom_jcl.tsv
 ```
