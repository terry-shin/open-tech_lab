from google.cloud import storage, bigquery
from lxml import html
import datetime

# スクレイピング実行日時
run_date = datetime.datetime.now().strftime('%Y-%m-%d %H:00:00')

# メイン
'''
# HTTPトリガー サンプル
# messageというパラメータが付与されていたら、それを返却する
def main(request):
    # url;パラメータをjson形式で取得
    request_json = request.get_json()

    # パラメータ配列を直接参照 & 判定
    if request.args and 'message' in request.args:
        return request.args.get('message')
    # json形式で取得したパラメータを参照 & 判定
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'
'''

# 指定のバケットにファイル作成・更新をトリガーとして起動
def main(event, context):
    print("sample function START")
    print(run_date)
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    # トリガーとなったファイルの情報をログに出力
    file = event
    print(f"Processing file: {context.event_type}.")
    print(f"Processing file: {file['name']}.")
    print(f"Processing bucket: {file['bucket']}.")
    print(f"Processing meta: {file['metageneration']}.")
    print(f"Processing created: {file['timeCreated']}.")
    print(f"Processing updated: {file['updated']}.")

    # 指定のファイルから解析用のhtmlを取得
    html_data = get_html(file)

    # サンプル：タイトルタグ取得
    test_str = html_data.xpath(".//title")
    # デバッグメッセージ
    print(len(test_str))
    if len(test_str) > 0:
        print(test_str[0].text)

        # bigquery登録
        # 処理したファイル名とタイトルタグをBigQueryに登録
        input_data = []
        input_data.append(file['name'])
        input_data.append(test_str[0].text)

        regist_data(input_data)

    print("sample function END")


# CloudStrageから
def get_html(file):

    # CloudStrage client定義
    storage_client = storage.Client()

    #bucketからファイル取得
    bucket = storage_client.get_bucket(file['bucket'])
    blob = bucket.blob(file['name'])

    #bucketからファイルをダウンロードしてopen(html ver)
    blob.download_to_filename("/tmp/test.html")
    input_file = "/tmp/test.html"
    html_parser = html.HTMLParser(encoding='utf-8')

    with open(input_file, mode='rb') as f:
        # パーサーを指定して解析
        html_data = html.fromstring(f.read(), parser=html_parser)

    return html_data

# bigquery 登録テスト用function
def regist_data(input_data):

    # bigqueryで利用するテーブル [project ID].[データセット名].[テーブル名]
    table_name = f"{プロジェクトID}.crawler_test.test_table"
    bigquery_client = bigquery.Client()

    # json形式でデータを登録
    insert_row = [
        {u"check_date": f"{run_date}", u"value1": f"{input_data[0]}", u"value2": f"{input_data[1]}"}
    ]

    errors = bigquery_client.insert_rows_json(table_name, insert_row) 
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))