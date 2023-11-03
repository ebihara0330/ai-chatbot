"""
title:
Blobデータから回答を生成するプロトタイプ

contents:
BlobからDBデータをDLして同データを元に回答を生成する

"""
import os
from datetime import datetime, timezone
from azure.storage.blob import BlobServiceClient, BlobClient
from prototype_base import PrototypeBase
from azure.storage.blob import BlobServiceClient

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
