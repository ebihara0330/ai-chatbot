"""
title:
外部API関連の処理を管理するプログラム

contents:
Mikkeからのデータ取得/変換機能などを提供する

"""
import os
import requests
import json
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter

logging.basicConfig(level=logging.DEBUG) 

class ExternalAPIManager():    

    def __init__(self, config):
        """
        各種初期化処理

        """
        self.config = config


    def search_mikke(self, prompt) :
        """
        プロンプトを使ったMikkeのAPI検索

        Args:
        prompt：chatbotUIの入力プロンプト

        Return:
        検索結果

        """
        url = "https://api.mikke.vacloudapps.com/v1/pollinatornetwork/search"
        api_key = os.environ.get('MIKKE')
        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
        data = {
            "_source": ["title" , "content"], 
            "query" : {
                "multi_match": {
                    "query": prompt,
                    "fields": [ "title", "content",  "filename"],
                    "operator": "or"
                }
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code == 200 :
            logging.debug(response.content)
        else :
            logging.error("api.mikke.vacloudapps.com status_code:" + str(response.status_code) + " " + response.text)

        return response.json()


    def is_exist(self, mikke_response) :
        """
        Mikkeの検索結果の有無を判定

        Args:
        response：Mikkeの検索結果

        Return:
        True 結果あり、False 結果なし

        """
        return 'hits' in mikke_response and bool(mikke_response['hits']['hits'])


    def create_documents(self, mikke_response) :
        """
        Mikkeの検索結果を使ったAIの入力データ作成

        Args:
        response：Mikkeの検索結果

        Return:
        AI入力用に加工したMikkeの検索データ

        """

        # データ取得
        title = mikke_response['hits']['hits'][0]['_source']['title']
        content = mikke_response['hits']['hits'][0]['_source']['content']

        # データ分割方法設定
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = self.config["chunk_size"],
            chunk_overlap  = self.config["chunk_overlap"],
            add_start_index = True,
        )

        # データ分割＆Vector登録用のデータ作成
        documents = text_splitter.create_documents(
            texts=[content[:self.config["external_data_limit"]]],
            metadatas=[{"title": title}])
        return documents
    