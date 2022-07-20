import os
import sys
import json
import requests

# バッチ処理用
import csv
import pandas as pd
import io
import gcsfs
import time
import datetime

import urllib.request

import mojimoji

# Cloud Strage
from google.cloud import storage

# 国税庁 csvレスポンスヘッダ
headers = ["sequenceNumber","corporateNumber","process","correct","updateDate","changeDate","name","nameImageId","kind","prefectureName","cityName","streetNumber","addressImageId","prefectureCode","cityCode","postCode","addressOutside","addressOutsideImageId", "closeDate", "closeCause", "successorCorporateNumber", "changeCause", "assignmentDate", "latest", "enName", "enPrefectureName", "enCityName", "enAddressOutside", "furigana", "hihyoji"]

# 出力結果ヘッッダ
output_headers = ["advertiser_id", "advertiser_code", "company_id", "check_name", "hit_count", "result…"]

# バケット名
bucket_name = "test_bucket"

def run(event, context):
    """
    run関数
    """
    fs = gcsfs.GCSFileSystem(project='GCPプロジェクト')

    # 定義ファイル取得
    with fs.open('test_bucket/batch/definition.json') as f:
        df_list = json.load(f)
        print(df_list["id"])
        print(df_list["coporatation_name"])

    # パラメータチェック　後ほど拡充
    if not df_list:
        print("no definition file")
        return
    elif not df_list["file_name"]:
        print("no input file")
        return

    si = io.StringIO()

    # target 1:あいまい 2:完全一致
    # mode   1:前方一致 2:部分一致
    url = "https://api.houjin-bangou.nta.go.jp/4/name?id=KPEzPdQnvAPvh&type=02&target={}&mode={}&name=".format(1,1)

    # 法人ファイル取得 
    check_count = 0
    with fs.open(bucket_name + '/batch/' + df_list["file_name"]) as f:
        df = pd.read_csv(f)
        result_w = csv.writer(si, quoting=csv.QUOTE_ALL)
        result_w.writerow(output_headers)

        for df_index, df_row in df.iterrows():
            if df_index%100 == 0:
                print(str(df_index) + "件目")

            output_str = [df_row["advertiser_id"], df_row["advertiser_code"], df_row["company_id"], df_row[df_list["coporatation_name"]]]
            check_name = df_row[df_list["coporatation_name"]]
            check_name = mojimoji.han_to_zen(df_row[df_list["coporatation_name"]], ascii=False)
            check_name = mojimoji.han_to_zen(df_row[df_list["coporatation_name"]], digit=False)
            check_name = mojimoji.han_to_zen(df_row[df_list["coporatation_name"]], kana=False)

            response = requests.get(url + check_name)
            df = pd.read_csv(io.BytesIO(response.content), sep=",", names=headers)

            for index, row in df.iterrows():
                if index <= 0:
                    output_str.append(row[1])
                elif index < 10:
                    # 10件以上は省略
                    output_str.append(str(row['corporateNumber']) + ":" + row['name'])

            result_w.writerow(output_str)
            # 国税庁側への負荷を減らす
            #time.sleep(0.05)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob("results/result_{}.csv".format(datetime.datetime.now()))
    blob.upload_from_string(si.getvalue(), content_type='text/csv')
