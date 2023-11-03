"""
title:
API検索を加味した回答生成用のプロトタイプ

contents:
mikkeから取得したデータとDBデータを加味したAI回答を生成する

"""
import logging
from prototype_base import PrototypeBase
logging.basicConfig(level=logging.DEBUG) 

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

        # mikkeからのデータ取得
        mikke_response = params.ext_api.search_mikke(params.prompt)

        # LLMに一時的な入力データを追加
        if params.ext_api.is_exist(mikke_response) :
            params.llm.add_documents(params.ext_api.create_documents(mikke_response))

        # カスタムプロンプト
        template = """文書が複数ある場合は、すべての文書を元に以下の質問に回答して
        
        質問：{question}"""

        # プロンプトへの回答を生成
        result = params.llm.request_answer(
            prompt=params.prompt, 
            template=template,
            history=params.history)
        
        return result
    
if __name__ == "__main__":
    Prototype().run()
