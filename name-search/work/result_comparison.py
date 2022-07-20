import json
import re
import datetime
from custom import checkCompanyClass as cc

def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return "None"

# 入出力ファイル
out_file_dir = './output/result_comparison_{}.tsv'.format(datetime.datetime.now())
MP_input_file_dir = './output/mp_result_20201214.tsv'
XONE_input_file_dir = './output/xone_result_20201214.tsv'


# 比較用配列組み込み
MP_input_file = open(MP_input_file_dir,'r',encoding='utf_8')
MP_line = MP_input_file.readline().strip()

MP_resut_list = {}
while MP_line:
    line_array = MP_line.split("\t")

    # 企業名と変換したものを入れる
    MP_resut_list[line_array[0]] = line_array[2]
    # 次の行へ
    MP_line = MP_input_file.readline().strip()


out_file = open(out_file_dir, 'w', encoding='utf_8_sig')
out_file.write('Xone広告主ID\tXone広告主名\t識別結果\t候補企業名\t法人番号\tmp広告主名\n')

# チェック対象ファイル読み込み
XONE_input_file = open(XONE_input_file_dir,'r',encoding='utf_8')
XONE_line = XONE_input_file.readline().strip()

while XONE_line:
    line_array = XONE_line.split("\t")
    XONE_check_result = "None"

    # 識別結果が×以外の結果照合
    if (line_array[2] == '○' or line_array[2] == '△') and line_array[3] in MP_resut_list.values():
        result_key = get_key_from_value(MP_resut_list, line_array[3])
        XONE_check_result = result_key

    #結果書き込み
    out_file.write('{}\t{}\n'.format(XONE_line, XONE_check_result))

    # 次の行へ
    XONE_line = XONE_input_file.readline().strip()

MP_input_file.close
XONE_input_file.close
out_file.close
