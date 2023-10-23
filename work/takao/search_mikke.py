"""
title:
MIKKEの検索API呼び出し処理

contents:
- 検索ワードから、API経由でMIKKE内の検索処理を行う。

実行方法:
- 右クリック > Run Python > Run Python File in Terminal 
"""
import requests
import json
import os

url = "https://api.mikke.vacloudapps.com/v1/pollinatornetwork/search"  # 使用するAPIのエンドポイント
api_key = os.environ.get('MIKKE') # 環境変数にapiキーを設定

# ヘッダ情報を辞書形式で作成
headers = {
    "X-API-KEY": api_key,
    "Content-Type": "application/json"
}

# mikke検索メソッド
def search(search_word):
    # POSTで送信するデータ
    data = {
        "_source": ["title" , "content"], # ここに返却して欲しい項目を入れる
        "query" : {
            "multi_match": {
                "query": search_word,
                "fields": [ "title", "content",  "filename"],
                "operator": "or"
            }
        }
    }

    # リクエストを送信。json.dumps()で辞書形式のデータをJSON文字列に変換
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # レスポンスをJSON形式に変換
    response_data = response.json()

    # レスポンスデータを表示
    # pprint.pprint(response_data) # 全データ
    title = response_data['hits']['hits'][0]['_source']['title']
    content = response_data['hits']['hits'][0]['_source']['content']
    result_dic = {'title': title, 'content': content}

    return result_dic

# 検索結果確認
mikke_search_text = "有給休暇"
result = search(mikke_search_text)
print('title: ' + result['title'])
print('content: ' + result['content'])