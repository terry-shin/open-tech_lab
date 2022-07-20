import os
import datetime

from google.cloud import bigquery,storage

bigquery_client = bigquery.Client()

#テーブル名指定
CRAWLER_ENV = os.environ.get('CRAWLER_ENV', 'local')
table_name = f"{GCPプロジェクト}.{CRAWLER_ENV}_ecpf_data_set.product_data"
bucket_uri = "gs://test-bucket/*.csv"

# メイン
# HTTPトリガー サンプル
def main(request):
    # url;パラメータをjson形式で取得
    request_json = request.get_json()

    export_query = f"""
        EXPORT DATA OPTIONS(
            uri='{bucket_uri}',
            format='CSV',
            overwrite=true,
            header=false,
            field_delimiter=','
        ) AS
        SELECT asin FROM `{table_name}`
    """

    export_job = bigquery_client.query(export_query)
    export_result = export_job.result()

    print(export_result)

    print("export bigquery table export END")
    return "Success"