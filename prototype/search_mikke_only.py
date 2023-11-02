"""
title:
API検索を加味した回答生成用のプロトタイプ

contents:
mikkeから取得したデータとDBデータを加味したAI回答を生成する

"""
from prototype_base import PrototypeBase
import chromadb
from langchain.vectorstores import Chroma

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

        # # mikkeからのデータ取得
        # mikke_response = params.ext_api.search_mikke(params.prompt)

        # # LLMに一時的な入力データを追加
        # if params.ext_api.is_exist(mikke_response) :
        #     params.llm.add_documents(params.ext_api.create_documents(mikke_response))

        # プロンプトへの回答を生成
        return super().llm.request_answer(prompt=params.prompt, history=params.history)

if __name__ == "__main__":
    PrototypeSample().run()
