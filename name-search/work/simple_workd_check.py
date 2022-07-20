import MeCab
import unicodedata
import pickle
import pandas as pd
import json
import re

from custom import checkCompanyClass as cc

# 辞書ファイル・クラス宣言
dic_file_dir = './custom_dic/custom_company_dic.pkl'
corp_file_dir = './custom_dic/custom_corporation_list.pkl'
check_company = cc.checkCompanyClass(dic_file_dir,corp_file_dir)

check_name = "カカオジャパン"

result_list = check_company.check_company_name(check_name)

print(result_list)

