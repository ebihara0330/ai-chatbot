"""
title:
LangChainを用いたChatGPT(Azure OpenAI)の呼び出し処理のサンプルプログラム

contents:
- 外部データ(CSV)を考慮した回答
- 会話履歴の保持

実行方法:
- 「環境変数を編集」から、環境変数「OPENAI_API_KEY」にAzure OpenAIのAPIキーを設定する。
- requirements.txtを再取り込みする。
- ローカルから検証UIを起動する。
"""
import logging
import os
import sys
sys.path.append(os.path.abspath("work"))
import prototype_common

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import AzureChatOpenAI

# Azure OpenAIの設定
api_type = "azure"
api_base = "https://dxcoeai-model.openai.azure.com/"
api_version = "2023-07-01-preview"
api_key = os.getenv("OPENAI_API_KEY")

# データ取得（CSV）
loader = CSVLoader("work/takao/test_data.csv",encoding="utf-8") # 外部データのテスト用データ
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# LLMの設定
llm = AzureChatOpenAI(openai_api_version=api_version,
                      openai_api_base=api_base,
                      openai_api_type=api_type,
                      deployment_name="gpt-35-turbo",
                      temperature=0)
embedding = OpenAIEmbeddings(openai_api_version=api_version,
                            openai_api_base=api_base,
                            openai_api_type=api_type,
                            deployment="text-embedding-ada-002") # embedding用のモデル「text-embedding-ada-002」を使用
memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)

#------------------------------------------------------------------------
# 全ファイルファイル取得処理.
#
# 指定ディレクトリ内のすべてのファイルのパスを取得する
#------------------------------------------------------------------------
def get_all_files(directory):
    file_list = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            d = directory
            file_list.append(os.path.join(root, filename))
    return file_list

db_dir_name = 'DB'
if not os.path.exists(db_dir_name):
    os.mkdir(db_dir_name)
db_dir = './' + db_dir_name
db = get_all_files(db_dir)

if not db:
    # ベクトルDBの作成
    db = Chroma.from_documents(texts, embedding, persist_directory = db_dir)
    # ベクトルデータをディレクトリに保存
    db.persist()
else:
    # 作成済みのベクトルDBを取得
    db = Chroma(persist_directory = db_dir, embedding_function=embedding)

retriever=db.as_retriever()

qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever(), memory=memory)
chat_history = []

#------------------------------------------------------------------------
# ChatGPT呼び出し.
#------------------------------------------------------------------------
def askChatGPT(question, history):
    # TODO 履歴削除時（プロトタイプ変更時）の処理実装
    answer = qa.run(question)

    return answer

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
        answer = askChatGPT(prompt, history)
        # AIの回答返却（returnでは戻らないため）
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