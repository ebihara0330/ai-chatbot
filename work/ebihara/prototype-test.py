"""
title:
プロトタイプ（検証UIからの実行サンプル1）

contents:
検証UIからの入出力を確認するサンプルプロトタイプ

"""
import logging
from prototype_base import PrototypeBase

class PrototypeSample(PrototypeBase):

    def run(self):
        """
        プロトタイプ実行

        Args:
            prompt: AIモデルへのプロンプト
            history: チャット履歴

        Returns:
            プロンプトへのAI回答

        """
        
        try:
            answer = self.askChatGPT()
            print(answer)
        except Exception as e:
            error = str(e)
            logging.error("An error occurred: %s", error) 
            print(error)

if __name__ == "__main__":
    PrototypeSample().run()
