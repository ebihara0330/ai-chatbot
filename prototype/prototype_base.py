"""
title:
coe-ai プロトタイプの基底処理

contents:
chatbotUIプロトタイプの基本的な枠組みを実装する

"""
import re
import os
import sys
import json
import yaml
import logging
import argparse
from typing import Optional, List, Dict, Any
from yaml.loader import SafeLoader

sys.path.extend([os.path.abspath("./"), os.path.abspath("util")])
from util.llm_manager import LlmManager
from util.external_api_manager import ExternalAPIManager

class PrototypeBase:

    class Params:
        """
        プロトタイプのパラメータ

        Args:
        config：langchain関連の設定
        llm：LLM関連のプログラム
        ext_api：外部API関連のプログラム
        prompt：検証UIから送信されたプロンプト
        history：チャット履歴
        """
        def __init__(
            self, 
            config: Dict[str, Any], 
            history: List[Any], 
            prompt: str, 
            ext_api: Optional[ExternalAPIManager], 
            llm: Optional[LlmManager]
        ):
            self.prompt = prompt
            self.history = history
            self.config = config
            self.ext_api = ext_api
            self.llm = llm


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


    def read_input(self):
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


    def make_params(self) -> Params:
        """
        プロトタイプパラメータ生成

        Return:
        プロトタイプパラメータ

        """
        # 設定ファイル取得
        with open('./config.yaml', 'r', encoding='utf-8') as file:
            config = yaml.load(file, Loader=SafeLoader)
            config=config['langchain']

        # パラメータ取得
        input = self.read_input()
        params = self.Params(
            prompt=input.prompt, 
            history=json.loads(input.history),
            config=config, 
            ext_api=ExternalAPIManager(config), 
            llm=LlmManager(config))
        return params


    def processing_structure(func):
        """
        プロトタイプ実行

        Contents:
        プロトタイプの基本的な枠組み（mainプロセスへの結果返却・エラーハンドリング）を実装する
        """
        def wrapper(self):
            try:
                # パラメータ生成
                params : PrototypeBase.Params = self.make_params()
                # VectorDBの最新化
                params.llm.modernize_vector_db()
                # プロトタイプ実行
                print(func(params))

            except Exception as e:
                # DBの作成者と利用者が違う場合は利用者をアップデート後にプロトタイプ実行
                if "InconsistentHashError" in str(e.add_note):
                    pattern = re.compile(r'[a-f0-9]{32}')
                    params.llm.update_migration(pattern.findall(str(e)))
                    print(func(params))
                # その他エラーはエラー内容を返却
                else :
                    logging.error(f"An error occurred in {func.__name__}: {str(e)}")
                    print(e)
            finally:
                # persistしなくても永続化される問題への対処で外部データを一律削除
                if hasattr(params.llm, 'temp_ids') :
                    params.llm.db.delete(self.llm.temp_ids)

        return wrapper

