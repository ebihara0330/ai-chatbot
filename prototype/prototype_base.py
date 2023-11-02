"""
title:
coe-ai プロトタイプの基底処理

contents:
chatbotUIプロトタイプの基本的な枠組みを実装する

"""
import logging
import argparse
import json
import sys
import os
import yaml
from yaml.loader import SafeLoader

sys.path.append(os.path.abspath("util"))
from llm_manager import LlmManager # type: ignore
from external_api_manager import ExternalAPIManager # type: ignore 

class PrototypeBase:

    def __init__(self):
        """
        初期設定

        Contents:
        プロトタイプ共通で利用する機能の初期設定

        """
        # ログの出力設定
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.StreamHandler()
            ]
        )


    def read_params(self):
        """
        ChatbotUIのパラメータ読み込み処理

        Return:
        プロンプト、チャット履歴

        """
        # mainProcessで設定されたパラメータ読み込み
        parser = argparse.ArgumentParser()
        parser.add_argument('prompt', type=str)
        parser.add_argument('history', type=str)
        parser.parse_args().history = json.loads(parser.parse_args().history)
        return parser.parse_args()


    def processing_structure(func):
        """
        プロトタイプの構造設定

        Contents:
        プロトタイプの基本的な枠組み（mainプロセスへの結果返却・エラーハンドリング）を実装する

        """
        def wrapper(self):
            try:
                # 設定ファイル読み込み
                with open('./config.yaml', 'r', encoding='utf-8') as file:
                    config = yaml.load(file, Loader=SafeLoader)
                    self.config = config['langchain']

                # パラメータ取得
                params = self.read_params()
                params.history = json.loads(params.history)
                params.ext_api = ExternalAPIManager(self.config)
                #params.llm = LlmManager(self.config, "gpt-35-turbo", "text-embedding-ada-002", "2023-07-01-preview")

                # プロトタイプ実行
                print(func(params))

            except Exception as e:
                # エラーの場合はエラー内容を返却
                logging.error(f"An error occurred in {func.__name__}: {str(e)}")
                print(e)
            finally:
                # persistしなくても永続化される問題への対処で外部データを一律削除
                if hasattr(params.llm, 'temp_ids') :
                    params.llm.db.delete(params.llm.temp_ids)

        return wrapper

