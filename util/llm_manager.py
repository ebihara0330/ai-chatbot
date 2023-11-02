"""
title:
LLM関連の処理を管理するプログラム

contents:
LLMのインスタンス生成および同LLMを利用した各種機能の提供を行う

"""

import logging
import chromadb

from langchain.vectorstores import Chroma
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings 
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.question_answering import load_qa_chain

logging.basicConfig(level=logging.DEBUG) 

class LlmManager():

    def __init__(self, config, llm, llm_embedding, api_version):
        """
        LLMの初期化

        Args:
        llm：利用するllmの名称
        llm_embedding：利用するllm(embedding)の名称
        api_version：llmのAPIバージョン

        """
        # 設定ファイル
        self.config = config

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

        # 回答生成
        qa = ConversationalRetrievalChain.from_llm(
            llm=self.llm, 
            retriever=self.db.as_retriever(search_kwargs={"k": 5}), 
            return_source_documents=True,
            return_generated_question=True,
            max_tokens_limit=self.config["input_token_limit"])
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