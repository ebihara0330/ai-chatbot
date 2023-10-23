"""
title:
coe-ai chatbotUIの共通処理実装用

contents:
プロトタイプ共通で使う処理を実装する

"""
import logging
import openai
import argparse
import json
import os

def read_params():
    """
    プロトタイプのパラメータ読み込み

    Returns:
        パラメータ（プロンプト、チャット履歴）が格納された配列

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('prompt', type=str)
    parser.add_argument('history', type=str)
    parser.parse_args().history = json.loads(parser.parse_args().history)
    return parser.parse_args()


def setup_logging():
    """
    プロトタイプのログ出力をセットアップ
    プロトタイプ内で同セットアップ処理を実行する

    """
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )


def generate_ai_answer(prompt):
    """
    AIの回答生成

    Args:
        prompt: AIモデルへのプロンプト

    Returns:
        プロンプトへのAI回答

    """
    openai.api_type = "azure"
    openai.api_base = "https://chatbot-ai-ebihara-public.openai.azure.com/"
    openai.api_version = "2023-07-01-preview"
    openai.api_key = "15a7d33c4f3b4149b33f7384fdc387e7"

    response = openai.ChatCompletion.create(
    engine="gpt-35-turbo",
    messages = [{"role":"system","content":"You are an AI assistant that helps people find information."},{"role":"user","content":prompt}],
    temperature=0.7,
    max_tokens=800,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None)
    return response['choices'][0]['message']['content']
