"""
title:
LangChainを用いたChatGPT(Azure OpenAI)の呼び出し処理のサンプルプログラム

contents:
- 外部データ(CSV)を考慮した回答

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
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts import PromptTemplate

# Azure OpenAIの設定
api_type = "azure"
api_base = "https://dxcoeai-model.openai.azure.com/"
api_version = "2023-07-01-preview"
api_key = os.getenv("OPENAI_API_KEY")

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

# Gitの管理外にベクトルDBのデータを配置
os.chdir('../')
db_dir = os.path.join('.', 'data/vector_db_data/DB')
db = Chroma(persist_directory = db_dir, embedding_function=embedding)

# 件数を指定する場合：　search_kwargs={"k": 10}
retriever=db.as_retriever(search_kwargs={"k": 5})

chat_history = []

#------------------------------------------------------------------------
# ChatGPT呼び出し.
#------------------------------------------------------------------------
def askChatGPT(question, history):
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    if not history:
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    
    # 関連性の高い上位のデータを取得
    relevant_documents = retriever.get_relevant_documents(query=question)

    # 回答作成に使用されるデータの一部を検証UIにprintする場合
    # print('\r\n')
    # print('回答に使用したデータ件数：')
    # print(len(relevant_documents))
    # for doc in relevant_documents:
    #     print('\r\n')
    #     print('-----------------------------------')
    #     print('\r\n')
    #     print(doc.page_content[:100])

    print('\r\n')
    
    custom_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. Please summarize the answer even if If you have different answers. Please insert a line break in appropriate places for readability.
    
    {question}"""

    CUSTOM_QUESTION_PROMPT = PromptTemplate.from_template(custom_template)

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        retriever=db.as_retriever(), 
        condense_question_prompt=CUSTOM_QUESTION_PROMPT,
        memory=memory)

    # TODO 履歴対応
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
        print('-----------------------------------')
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