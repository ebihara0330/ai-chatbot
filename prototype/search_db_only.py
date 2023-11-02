"""
title:
API検索を加味した回答生成用のプロトタイプ

contents:
mikkeから取得したデータとDBデータを加味したAI回答を生成する

"""
from prototype_base import PrototypeBase

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

        # アクセスするURL
        url = 'https://mzbotstorage.blob.core.windows.net/root/test.txt?sp=r&st=2023-11-02T09:27:37Z&se=2024-11-02T17:27:37Z&spr=https&sv=2022-11-02&sr=b&sig=xR0U0p68A0QjA41Vr%2Fd1lRNp1cceR6rZeeFNP2Zsk8w%3D'

        # GETリクエストを発行
        response = requests.get(url)

        # レスポンスコードを確認 (200は成功を意味します)
        print(response.status_code)

        # HTMLコンテンツを表示
        print(response.text)
        return "params.llm.request_answer(prompt=params.prompt, history=params.history)"
    
if __name__ == "__main__":
    PrototypeSample().run()
