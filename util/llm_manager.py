"""
title:
LLM関連の処理を管理するプログラム

contents:
LLMのインスタンス生成および同LLMを利用した各種機能の提供を行う

"""

import os
import re
import sqlite3
import logging
import chromadb

from langchain.vectorstores import Chroma
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings 
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient

logging.basicConfig(level=logging.DEBUG) 

class LlmManager():

    def __init__(self, config):
        """
        LLMの初期化

        Args:
        config：langchain関連の設定ファイル

        """
        # 設定ファイル
        self.config = config


    def set_model(self, llm, llm_embedding, api_version):
        """
        モデル情報設定

        Args:
        llm：利用するllmの名称
        llm_embedding：利用するllm(embedding)の名称
        api_version：llmのAPIバージョン

        """
        # LLM定義
        api_type = "azure"
        api_base = "https://chatbot-ai-ebihara-public.openai.azure.com/"

        # AI情報取得
        self.llm = AzureChatOpenAI(
            openai_api_version=api_version,
            openai_api_base=api_base,
            openai_api_type=api_type,
            deployment_name=llm,
            temperature=0,
            max_tokens=self.config["max_tokens"])
        
        # AI情報取得（質問文再構築用）
        self.question_rearrange_llm = AzureChatOpenAI(
            openai_api_version=api_version,
            openai_api_base=api_base,
            openai_api_type=api_type,
            deployment_name=llm,
            temperature=0,
            max_tokens=self.config["max_tokens"])

        # AI(Embedding)情報取得
        self.embedding = OpenAIEmbeddings(
            openai_api_version=api_version,
            openai_api_base=api_base,
            openai_api_type=api_type,
            deployment=llm_embedding)

        # vectorDB取得
        self.db = Chroma(
            client=chromadb.PersistentClient(path='./DB'),
            embedding_function=self.embedding) 


    def add_documents(self, data) :
        """
        入力テキストを回答生成の入力データに追加

        Return:
        データIDのList

        """
        self.temp_ids = self.db.add_documents(data)
    

    def similarity_search(self, prompt, top_k) :
        """
        検索に使用するデータを指定した件数分取得

        """
        result = self.db.similarity_search(prompt, top_k=top_k)
        return result


    def request_answer(self, **kwargs) :
        """
        プロンプトに対する回答を生成

        Args:
        prompt：chatbotUIの入力プロンプト

        """
        # カスタムプロンプト設定
        if "template" in kwargs:
            question = PromptTemplate(
                template = kwargs["template"],
                input_variables=["question"]
            )
            kwargs["prompt"] = question.format(question=kwargs["prompt"])

        # チャット履歴作成
        chat_history = []
        if "history" in kwargs:
            for chat in kwargs["history"]:
                chat_history.append((chat['prompt'], chat['answer']))

        # 回答生成
        qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm, 
            retriever=self.db.as_retriever(search_kwargs={"k": 5}), 
            return_source_documents=True,
            return_generated_question=True,
            max_tokens_limit=self.config["input_token_limit"],
            condense_question_llm=self.question_rearrange_llm,
            )
        result = qa({"question": kwargs["prompt"], "chat_history": chat_history})
        logging.debug(result)

        return result['answer']
    
    # TODO 問題なければ、request_answerを以下に置き換える。
    def request_answer_with_history(self, **kwargs) :
        """
        プロンプトに対する回答を生成

        Args:
        prompt：chatbotUIの入力プロンプト

        """
        # カスタムプロンプト設定
        if "template" in kwargs:
            question = PromptTemplate(
                template = kwargs["template"],
                input_variables=["question"]
            )
            kwargs["prompt"] = question.format(question=kwargs["prompt"])

        # チャット履歴作成
        chat_history = []

        if "history" in kwargs:
            for chat in kwargs["history"]:
                chat_history.append((chat['prompt'], chat['answer']))


        # 回答生成
        qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm, 
            retriever=self.db.as_retriever(search_kwargs={"k": 5}), 
            return_source_documents=True,
            return_generated_question=True,
            max_tokens_limit=self.config["input_token_limit"],
            condense_question_llm=self.question_rearrange_llm,
            )
        result = qa({"question": kwargs["prompt"], "chat_history": chat_history})
        logging.debug(result)

        return result['answer']
    

    def modernize_vector_db(self) :
        """
        ベクトルDBの最新化

        Contents:
        Blobに格納したDBファイルを元にローカルDBを最新化する

        """
        # Blob接続情報取得
        connection_string = "DefaultEndpointsProtocol=https;AccountName=mzbotstorage;AccountKey=55enF2UEzMTFtjn9mpg9TPvSgNpWgULSLkj0U3ErPYZhjwoNnQQoRoW6JzszuHO31h+sz0P2XaZ8+ASt0rOc+Q==;EndpointSuffix=core.windows.net"
        container_name = "root"
        blob_name = self.config["db_path"]
        download_path = "./DB/chroma.sqlite3"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # 2回目以降（DBディレクトリ作成済）
        if os.path.exists(download_path):
            # blobの更新日付の方が新しければblobDBで置き換え
            local_last_modified = datetime.fromtimestamp(os.path.getmtime(download_path), tz=timezone.utc)
            blob_last_modified = blob_client.get_blob_properties()['last_modified']
            if blob_last_modified > local_last_modified:
                self.donwload_vector_db(blob_client, download_path)
        # 初回（DBディレクトリ未作成）
        else :
            # 一律blobDBをダウンロード
            os.makedirs("DB")
            self.donwload_vector_db(blob_client, download_path)


    def donwload_vector_db(self, blob_client, download_path):
        """
        ベクトルDBのダウンロード処理

        Args:
        blob_client：blob情報
        download_path：ダウンロードするDBファイルのパス

        """
        with open(download_path, "wb") as download_file:
            logging.debug("-----------------------------------------")
            logging.debug("download_file.write:" + str(download_path))
            logging.debug("-----------------------------------------")
            download_file.write(blob_client.download_blob().readall())


    def update_migration(self, hashes):
        """
        DB利用者の更新処理

        Contents:
        ChromaはHash値を使ってDBの作成者と利用者の整合チェックを行っている
        処理が同じでもローカル⇔サーバのオブジェクト差異でエラーになるため、
        ローカルで作成したDBをサーバ側で利用できるよう、不整合を解消する処理を実装する

        """
        try:
            # 利用者を作成者→現在の利用者にアップデートする
            conn = sqlite3.connect('DB/chroma.sqlite3', uri=True)
            cur = conn.cursor()
            cur.execute(f"UPDATE migrations SET hash = '{hashes[1]}' WHERE hash = '{hashes[0]}';")
            conn.commit()
            conn.close()

        except Exception as e:
            # エラーの場合はエラー内容を返却
            logging.error(f"An error occurred in {__name__}: {str(e)}")
            print(e)
