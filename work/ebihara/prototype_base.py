"""
title:
coe-ai chatbotUIの共通処理実装用

contents:
プロトタイプ共通で使う処理を実装する

"""
import logging
import openai
import argparse
import json
import os
from azure.storage.blob import BlobServiceClient
import logging
import openai
import argparse
import json
import os
from azure.storage.blob import BlobServiceClient
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader

from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
import os
import sys
import shutil

class PrototypeBase:

    def __init__(self):
        """
        プロトタイプのパラメータ読み込み

        Returns:
            パラメータ（プロンプト、チャット履歴）が格納された配列

        """
        parser = argparse.ArgumentParser()
        parser.add_argument('prompt', type=str)
        parser.add_argument('history', type=str)
        parser.parse_args().history = json.loads(parser.parse_args().history)
        params = parser.parse_args()
        self.prompt = params.prompt
        self.history = params.history
        self.setup_logging()
  #      self.get_blob()

    def run(self):
        pass

    def askChatGPT(self):
        openai.api_type = os.environ["OPENAI_API_TYPE"] = "azure"
        openai.api_base = os.environ["OPENAI_API_BASE"] = "https://chatbot-ai-ebihara-public.openai.azure.com/"
        openai.api_version = os.environ["OPENAI_API_VERSION"] = "2023-07-01-preview"
        openai.api_key = os.environ["OPENAI_API_KEY"] = "15a7d33c4f3b4149b33f7384fdc387e7"

       # LLMの設定
        llm = AzureChatOpenAI(openai_api_version=openai.api_version,
                            openai_api_base=openai.api_base,
                            openai_api_type=openai.api_type,
                            deployment_name="gpt-35-turbo",
                            temperature=0)
        embedding = OpenAIEmbeddings(deployment="text-embedding-ada-002") # embedding用のモデル「text-embedding-ada-002」を使用
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

        # データ取得（CSV）
        self.delete_all_files_in_directory()
        loader = CSVLoader("work/takao/test_data.csv",encoding="utf-8") # 外部データのテスト用データ
        texts = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        documents = text_splitter.create_documents([doc.page_content for doc in texts])
        # ベクトルDBの作成
        db = Chroma.from_documents(documents, embedding, persist_directory = './DB')
        # ベクトルデータをディレクトリに保存
        db.persist()
        db = Chroma(persist_directory = './DB', embedding_function=embedding)
        qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever(), memory=memory)
        answer = qa.run(self.prompt)

        return answer

    def delete_all_files_in_directory(self):
        # ディレクトリ内のファイルとサブディレクトリのリストを取得
        for filename in os.listdir("./DB"):
            file_path = os.path.join("./DB", filename)
            # ファイルの場合は削除
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            # ディレクトリの場合は再帰的に削除
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)

    def setup_logging(self):
        """
        プロトタイプのログ出力をセットアップ
        プロトタイプ内で同セットアップ処理を実行する

        """
        logging.basicConfig(
            level=logging.ERROR,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )

    def get_blob(self):
        connection_string = "DefaultEndpointsProtocol=https;AccountName=mzbotstorage;AccountKey=55enF2UEzMTFtjn9mpg9TPvSgNpWgULSLkj0U3ErPYZhjwoNnQQoRoW6JzszuHO31h+sz0P2XaZ8+ASt0rOc+Q==;EndpointSuffix=core.windows.net"  # Azure Portal から取得する
        container_name = "root"
        blob_name = "DB/chroma.sqlite3"
        download_path = "./DB/chroma.sqlite3"

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        directory = os.path.dirname(download_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
