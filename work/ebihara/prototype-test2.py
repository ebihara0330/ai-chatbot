"""
title:
プロトタイプ（検証UIからの実行サンプル1）

contents:
検証UIからの入出力を確認するサンプルプロトタイプ（セレクトボックスを複数した場合の動作確認用）

"""
import logging
import sys
import os

sys.path.append(os.path.abspath("work"))
import prototype_common

def run(prompt, history):
    """
    プロトタイプ実行

    Args:
        prompt: AIモデルへのプロンプト
        history: チャット履歴

    Returns:
        プロンプトへのAI回答

    """

    try:
        # ログのセットアップ
        prototype_common.setup_logging()
        # AIの回答生成
        answer = prototype_common.generate_ai_answer(prompt)
        # AIの回答設定（returnでは戻らない模様）
        print(answer)
    except Exception as e:
        error = str(e)
        logging.error("An error occurred: %s", error) 
        print(error)

if __name__ == "__main__":
    # 起動元パラメータ取得
    params = prototype_common.read_params()
    # 起動元パラメータ設定
    run(params.prompt, params.history)
