"""
title:
API検索を加味した回答生成用のプロトタイプ

contents:
mikkeから取得したデータとDBデータを加味したAI回答を生成する

"""
from prototype_base import PrototypeBase
import chromadb
from langchain.vectorstores import Chroma

class Prototype(PrototypeBase):

    @PrototypeBase.processing_structure
    def run(params : PrototypeBase.Params):
        """
        プロトタイプ

        Args:
        入力パラメータ群
        Returns:
        プロンプトに対するAIの回答
        """
        # モデル情報を設定
        params.llm.set_model("gpt-35-turbo", "text-embedding-ada-002", "2023-07-01-preview")

        # vectorDB取得
        params.llm.db = Chroma(
            client=chromadb.PersistentClient(path='./Dummy'),
            embedding_function=params.llm.embedding)

        # mikkeからのデータ取得
        mikke_response = params.ext_api.search_mikke(params.prompt)

        # LLMに一時的な入力データを追加
        if params.ext_api.is_exist(mikke_response) :
            params.llm.add_documents(params.ext_api.create_documents(mikke_response))

        # プロンプトへの回答を生成
        return params.llm.request_answer(prompt=params.prompt, history=params.history)

if __name__ == "__main__":
    Prototype().run()
