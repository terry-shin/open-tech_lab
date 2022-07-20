# db
from model.db import ProductData

def main(request):
    # url;パラメータをjson形式で取得
    request_json = request.get_json()

    # パラメータ配列を直接参照 & 判定
    if request.args and 'asin' in request.args:
        asin = request.args.get('asin')

        if ProductData.check_asin_exist(asin):
            return f"{asin}：product_data exist"
        else:
            return f"{asin}：no product_data"
    elif request_json and 'asin' in request_json:
        if ProductData.check_asin_exist(request_json['asin']):
            return f"{request_json['asin']}：product_data exist"
        else:
            return f"{request_json['asin']}：no product_data"
    else:
        return 'no asin!'
