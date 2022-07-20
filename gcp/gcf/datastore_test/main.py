import os
import datetime

from google.cloud import datastore

datasotre_client = datastore.Client()

#テーブル名指定
CRAWLER_ENV = os.environ.get('CRAWLER_ENV', 'local')
entity_name = f"{CRAWLER_ENV}-products"

# メイン
# HTTPトリガー サンプル
def main(request):
    # url;パラメータをjson形式で取得
    request_json = request.get_json()

    asin = "ABCD123"
    product_name = "ビールZZZ"

    # デバッグメッセージ
    # bigquery 一時テーブル登録
    input_data = []
    input_data.append(asin)
    input_data.append(product_name)
    regist_data(input_data)

    print("sample function END")
    return "Success"

def regist_data(input_data):

    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        product_key = datasotre_client.key(entity_name, input_data[0])

        entity = datastore.Entity(key=product_key)
        entity.update(
            {
                "product_name": input_data[1],
                "created_at": current_datetime
            }
        )
        datasotre_client.put(entity)
    except Exception as e:
        print(e)
