import os
import requests
import json

url = os.getenv("SLACK_WEBHOOK")

def hello_world(request):

    headers = {
        'Content-Type': 'application/json'
    }
    # payload = ('{"text": "gcp-slack連携テスト"}').encode('utf8')

    payload = {}
    payload["fallback"] = "テスト実行\nテスト <https://amazon.co.jp|確認>"
    payload["pretext"] = "テスト実行\nテスト <https://amazon.co.jp|確認>"    
    payload["text"] = "本文ここ\n改行チェック"    
    payload["color"] = "" 
    #payload["fields"] = []
    #payload["fields"].append({"title": "テストメッセージ", "value": "あぶない", "short": False})

    send_data = {"username": "gcf", "attachments": [payload]}

    response = requests.request("POST", url, headers=headers, data=json.dumps(send_data).encode('utf8'))

    print(response.text.encode('utf8'))
    return "success"