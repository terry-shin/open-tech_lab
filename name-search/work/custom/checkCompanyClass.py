import MeCab
import unicodedata
import pickle
import pandas as pd
import re

# 企業名識別Class
class checkCompanyClass():

    def __init__(self, dic_dir, corp_dir):
        # 企業名辞書
        self.company_name_list = pd.read_pickle(dic_dir)
        self.corpration_num_list = pd.read_pickle(corp_dir)

    # 企業名識別
    def check_company_name(self, check_name):

        # 部分一致対象の文字数
        check_max_len = 4
        check_name_len = len(check_name)

        # 文字列 前処理
        print("変換前ネーム：" + check_name)
        check_name = self.preprocess_check_name(check_name)
        print("変換後ネーム" + check_name)
        company_name = ''

        if check_name not in self.company_name_list.index:
            #ノイズとなりそうな文字を除去して再チェック
            re_check_name = re.sub(r'[-・ 　‐]','',check_name)
            if re_check_name in self.company_name_list.index:
                company_name = self.company_name_list.loc[re_check_name, 'value']
            elif check_name_len >= check_max_len:
                # 一定文字数[check_max_len]以上の場合のみ、部分一致で検索
                company_name = self.check_partial_match(check_name)
        else:
            company_name = self.company_name_list.loc[check_name, 'value']

        return_array = {"name": "","num": ""}
        return_array["name"] = company_name
        target_list = company_name.split(",")

        if len(target_list) > 1:
            for cnm in target_list:
                if cnm in self.corpration_num_list.index:
                    if return_array["num"] != "": return_array["num"] += ":" 
                    return_array["num"] += str(self.corpration_num_list.loc[cnm, 'value'])
        
        elif company_name in self.corpration_num_list.index:
            return_array["num"] = self.corpration_num_list.loc[company_name, 'value']

        return return_array


    # 部分一致チェック
    def check_partial_match(self, check_name):
        company_name = ''

        ##部分一致
        check_result = self.company_name_list.loc[self.company_name_list.index.str.startswith(check_name), 'value']

        # 必要であれば、取得してきたvalueの精査をする
        if len(check_result) >= 1:
            company_name = str(check_result[0])
        return company_name


    def preprocess_check_name(self, check_name):
        """
        法人名識別前処理 文字列加工

        Parameters
        ----------
        check_name : str
            識別対象_法人名文字列

        Returns
        -------
        check_name : str
        加工後 識別対象_法人名文字列
        """

        # チェック対象文字列の整備
        check_name = unicodedata.normalize('NFKC', check_name)
        check_name = self.delete_office_string(self.delete_incomplete_brackets(self.delete_brackets(self.replase_office_string(check_name))))

        return check_name

    def delete_brackets(self, check_name):
        """
        カッコ文字列除去

        Parameters
        ----------
        check_name : str
            識別対象_法人名文字列

        Returns
        -------
        check_name : str
        加工後 識別対象_法人名文字列
        """

        table = {
            "(": "（",
            ")": "）",
            "<": "＜",
            ">": "＞",
            "{": "｛",
            "}": "｝",
            "[": "［",
            "]": "］"
        }
        for key in table.keys():
            check_name = check_name.replace(key, table[key])

        l = ['（[^（|^）]*）', '【[^【|^】]*】', '＜[^＜|^＞]*＞', '［[^［|^］]*］',
            '「[^「|^」]*」', '｛[^｛|^｝]*｝', '〔[^〔|^〕]*〕', '〈[^〈|^〉]*〉']
        for l_ in l:
            check_name = re.sub(l_, "", check_name)

        return self.delete_brackets(check_name) if sum([1 if re.search(l_, check_name) else 0 for l_ in l]) > 0 else check_name


    def delete_incomplete_brackets(self, check_name):
        """
        中途半端カッコの除去

        Parameters
        ----------
        check_name : str
            識別対象_法人名文字列

        Returns
        -------
        check_name : str
        加工後 識別対象_法人名文字列
        """

        substr_idx = re.search(r"（", check_name)
        if substr_idx != None and substr_idx.start() > 0:
            check_name = check_name[0:substr_idx.start()]
        substr_idx = re.search(r"^(?!（).+）", check_name)
        if substr_idx != None and substr_idx.start() == 0:
            check_name = check_name[substr_idx.end():]

        return check_name


    def replase_office_string(self, check_name):
        """
        (株)対策
        『(株)』および『株)』を『株式会社』に置換

        Parameters
        ----------
        check_name : str
            識別対象_法人名文字列

        Returns
        -------
        check_name : str
        加工後 識別対象_法人名文字列
        """

        office_string_list = ['(株)', '株)']

        for office_string in office_string_list:
                check_name = check_name.replace(office_string, '株式会社')
        return check_name


    def delete_office_string(self, check_name):
        """
        市町村系法人対策
        役所などは、「〇〇市」などで法人登録されているので、その対策

        Parameters
        ----------
        check_name : str
            識別対象_法人名文字列

        Returns
        -------
        check_name : str
        加工後 識別対象_法人名文字列
        """

        office_string_list = ['役所', '役場', '庁', '生協']

        for office_string in office_string_list:
            check_pattern = r'.*({0})$'.format(office_string)
            if re.search(office_string, check_name):
                check_name = check_name.replace(office_string, '')
                break
        return check_name