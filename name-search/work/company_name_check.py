import json
import re
import datetime
import time
import sys

import csv

from custom import checkCompanyClass as cc
from tqdm import tqdm

# 処理前の時刻
start_time = time.time()

# 辞書ファイル・クラス宣言
dic_file_dir = './custom_dic/custom_company_dic.pkl'
corp_file_dir = './custom_dic/custom_corporation_list.pkl'
check_company = cc.checkCompanyClass(dic_file_dir,corp_file_dir)

# 入出力ファイル
# inputは引数で取得
# 例：$ python company_name_check.py ./data/HDY_2019.csv
args = sys.argv
input_file_dir = args[1]
if len(args) >= 3:
    check_col = int(args[2])
else: 
    check_col=0
if len(args) >= 4:
    id_col = int(args[3]) 
else: 
    id_col = False
out_file_dir = './output/company_name_check_result_{}.tsv'.format(datetime.datetime.now())

# 出力ファイル読み込み
out_file = open(out_file_dir, 'w', encoding='utf_8_sig')
out_file.write('No\tチェック対象\t識別結果\t候補企業名\t法人番号\n')

# 入力ファイル読み込み
#input_file = open(input_file_dir,'r',encoding='utf_8')
#line = input_file.readline().strip()

# result用
company_count = 0
ok_count = 0
mul_count = 0
ng_count = 0

# 結果格納配列
result_list = {}
id_list = {}
conflict_list = []

"""
while line:
    line_array = line.split(",")
    if line_array[check_col] in result_list:
        conflict_list.append(line_array[check_col])
        print(f"重複あり:{line_array[check_col]}")

    result_list[line_array[check_col]] = check_company.check_company_name(line_array[check_col])
    if id_col >= 0:
        id_list[line_array[check_col]] = line_array[id_col]
        print(line_array[id_col])

    # 次の行へ
    line = input_file.readline().strip()
"""


with open(input_file_dir, "r", newline="") as f:
    # 書き込みと同じ設定（delimiterとquotechar）を指定します.
    reader = csv.reader(f, delimiter=",", quotechar='"')
    for line_array in reader:
        if line_array[check_col] in result_list:
            conflict_list.append(line_array[check_col])
            print(f"重複あり:{line_array[check_col]}")

        result_list[line_array[check_col]] = check_company.check_company_name(line_array[check_col])
        if id_col >= 0:
            id_list[line_array[check_col]] = line_array[id_col]
            print(line_array[id_col])



# 処理前の時刻
check_time = time.time()
# 経過時間を表示
print(f"途中経過時間：{check_time - start_time}")

for ckn, cmn in tqdm(result_list.items()):
    company_count += 1

    # 結果をOK(一意のもの)、MUL(複数候補あり)、NG(候補なし)に振り分け
    if len(cmn["name"]) == 0:
        check_result = '×'
        ng_count+=1
        # NGだった場合は、「候補なし」をセットしておく
        cmn["name"] = '候補無し'
        cmn["num"] = 'None'
    else:
        check_result = '○'
        ok_count+=1

        # 複数候補ありの場合は、MULに結果上書き
        if len(cmn["name"].split(",")) > 1:
            check_result = '△'
            mul_count+=1

    #結果書き込み
    if len(id_list) > 0:
        result_no = id_list[ckn]
    else:
        result_no = company_count

    out_file.write('{0}\t{1}\t{2}\t{3}\t"{4}"\n'.format(result_no,ckn,check_result,cmn["name"],cmn["num"]))

# 集計結果書きこみ
out_file.write('OK/MUL\t{}\t{}\n'.format(ok_count,mul_count))
out_file.write('NG\t{}\n'.format(ng_count))
out_file.write('total\t{}\n'.format(company_count))
out_file.write('conflict\t{}\n'.format(len(conflict_list)))
for conflict_name in conflict_list:
    out_file.write('{}\n'.format(conflict_name))


out_file.close

# 処理前の時刻
end_time = time.time()
# 経過時間を表示
print(f"処理時間：{end_time - start_time}")
