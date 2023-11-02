"""
title:
API検索を加味した回答生成用のプロトタイプ

contents:
mikkeから取得したデータとDBデータを加味したAI回答を生成する

"""
from prototype_base import PrototypeBase
import socket
import os
import sys

sys.path.append(os.path.abspath("prototype"))
from prototype_base import PrototypeBase
from azure.storage.blob import BlobServiceClient
class PrototypeSample(PrototypeBase):
    @PrototypeBase.processing_structure
    def run(params):
        """
        プロトタイプ実行

        Args:params
        └ config：langchain関連のプロジェクト設定（config.yaml）
        └ llm：LLM関連のプログラム
        └ ext_api：外部API関連のプログラム
        └ prompt：検証UIから送信されたプロンプト
        └ history：チャット履歴

        Returns:
        プロンプトへのAI回答
        """
        import requests
        connection_string = "DefaultEndpointsProtocol=https;AccountName=mzbotstorage;AccountKey=55enF2UEzMTFtjn9mpg9TPvSgNpWgULSLkj0U3ErPYZhjwoNnQQoRoW6JzszuHO31h+sz0P2XaZ8+ASt0rOc+Q==;EndpointSuffix=core.windows.net"  # Azure Portal から取得する
        container_name = "root"
        blob_name = "test.txt"
        download_path = "./test.txt"

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        directory = os.path.dirname(download_path)
        
        print(blob_client)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
            print(download_file)

        super().config
        # アクセスするURL
        url = 'https://mzbotstorage.blob.core.windows.net/root/test.txt?sp=r&st=2023-11-02T09:27:37Z&se=2024-11-02T17:27:37Z&spr=https&sv=2022-11-02&sr=b&sig=xR0U0p68A0QjA41Vr%2Fd1lRNp1cceR6rZeeFNP2Zsk8w%3D'

        # GETリクエストを発行
        response = requests.get(url)

        ip_address = socket.gethostbyname('ai-chatbot-app.azurewebsites.net')
        print(ip_address)
        # レスポンスコードを確認 (200は成功を意味します)
        print(response.status_code)

        # HTMLコンテンツを表示
        print(response.text)
        return "params.llm.request_answer(prompt=params.prompt, history=params.history)"
    
if __name__ == "__main__":
    PrototypeSample().run()
