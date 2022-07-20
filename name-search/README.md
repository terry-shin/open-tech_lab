# custom_jcl_toolsについて

- 国税庁の企業データから、カスタム企業名辞書を生成する
- inputされた企業名に対して、辞書を検索して、登記されている企業名を抽出する

## 構成

[ディレクトリ構成]
```
custom_jcl_tools
│
├── work  # python
│   ├── custom      #独自Class格納dir
│   ├── custom_dic  #カスタム辞書格納dir
│   ├── custom_jcl  #tisのdic生成処理をカスタマイズしたものを格納
│   ├── input        #inputファイル格納dir
│   ├── output      #inputファイル格納dir
│   └── work直下     #各種pythonファイル
├── nta_api_use_batch  # 国税庁APIをつかった法人名識別(CloudFunctions)     
└── READMEやローカル検証様Dockerファイル

```
[work直下 pythonファイル]
- simple_workd_check.py
  - ロジック検証用
- make_custom_dic_file.py
  - 企業辞書生成
- company_name_check.py
  - inputに配置したファイルから企業識別を実施する
- result_comparison.py
  - 2つの識別結果付き合わせ用

## 利用方法

※localのpython環境手順は省略

### 独自企業辞書の生成
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

カスタム辞書を生成
 ```
 $ cd ../
 $ python tools/custom_jcl_save.py

# 以下にカスタム法人名 辞書ファイル生成
custom_dic/custom_company_dic.pkl
custom_dic/custom_corporation_list.pkl
 ```

### 法人名識別

※ workディレクトリ直下で作業

input対象をdataディレクトリに配置
  - CSV形式

識別処理の実行
```
$ python company_name_check.py [inputファイルpath] [識別する法人名のカラム] [IDとして扱いたいカラム]

# いかに処理結果が出力される
# 出力形式はTSV
./output
```

※識別する法人名が重複する場合は、一つに纏まる。ただしIDの指定がある場合は後勝ち。
