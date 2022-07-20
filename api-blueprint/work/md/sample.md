# Group 名寄せ

## 名寄せAPI [/v1/name_identification]

### 法人情報取得 [GET /v1/name_identification/{system_division}/{corporate_id}]
#### 処理概要
* 問い合わせされた法人の情報を返す
* システム区分 + 法人IDから、法人を特定する
    * 法人名のみのAPIも必要に応じて用意

+ Parameters
    + system_division: `x1` (string) - システム区分
    + corporate_id: `x00001` (string) - 法人ID

+ Response 200 (application/json)
    + Attributes
        + corporate_number: `1234567890123` (number) - 法人番号
        + corporate_name: `株式会社テスト` (string) - 法人名
        + corporate_kind: `301` (number) - 法人種別
        + corporate_name_kana: `テスト` (string) - 法人名_フリガナ
        + corporate_name_en: `テスト` (string) - 法人名_英語表記
        + prefecture_naame: `テスト` (string) - 所在地(都道府県)

### 法人ID登録 [POST]
#### 処理概要
* 渡されたチェック対象法人名から、正式法人名を識別し、法人番号と法人IDのマッピングを行う
    * マッピング情報は法人DBに登録
    * チェック対象法人名から、一意に法人を絞り込めなかった場合は、候補となる法人番号・法人名を返却する
        * その場合は、法人DBへの登録は実施しない
* 一旦、リアルタイムでのレスポンスを前提とする
    * 大量データの場合は非同期でのバルク処理を検討

+ Request (application/json)
    + Attributes
        + system_division: `x1` (string, required) - システム区分
        + corporate_list (array[object], fixed-type)
            + (object)
                + check_name: `テスト` (string, required) - チェック対象法人名
                + corporate_id: `x00001` (string, required) - 法人ID
            + (object)
                + check_name: `テスト2` (string, required) - チェック対象法人名
                + corporate_id: `x00002` (string, required) - 法人ID

+ Response 200 (application/json)
    + Attributes
        + corporate_list (array[object], fixed-type)
            + (object)
                + check_name: `テスト` (string, required) - チェック対象法人名
                + corporate_id: `x00001` (string) - 法人ID
                + corporate_number: `1234567890123` (number) - 法人番号
                + corporate_name: `株式会社テスト` (string) - 法人名
                + result_code: `1` (number) - 登録結果(0:NG,1:登録OK,2:複数候補あり )
            + (object)
                + check_name: `テスト2` (string, required) - チェック対象法人名
                + corporate_id: `x00002` (string) - 法人ID
                + corporate_number: `9876543212345,6546543212345` (number) - 法人番号
                + corporate_name: `株式会社テスト2,テスト2株式会社` (string) - 法人名
                + result_code: `2` (number) - 登録結果(0:NG,1:登録OK,2:複数候補あり )
