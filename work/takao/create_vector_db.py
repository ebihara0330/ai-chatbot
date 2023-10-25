"""
title:
ベクトルDB作成処理

contents:
- ファイル読み込み・ベクトルDB作成用CSVデータ作成処理を呼び出す。
- ベクトルDBを作成する。
※ 同じデータから何度もベクトルDBが作成されるリスクを回避するため、検証UIからのチャットで呼ばれる処理とは分離している。

実行方法:
- 右クリック > Run Python > Run Python File in Terminal 
"""
import file_reader
import os

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import AzureChatOpenAI

# ファイル読み込み・ベクトルDB作成用CSVデータ作成処理
csv_path = file_reader.create_csv_for_vector_db()
csv_directory = os.path.dirname(csv_path)
print(csv_directory)

# Azure OpenAIの設定
api_type = "azure"
api_base = "https://dxcoeai-model.openai.azure.com/"
api_version = "2023-07-01-preview"
api_key = os.getenv("OPENAI_API_KEY")

# データ取得（CSV）
loader = CSVLoader(csv_path,encoding="utf-8") # 外部データのテスト用データ
documents = loader.load()

text_splitter = CharacterTextSplitter(chunk_size=2000, chunk_overlap=0, separator="\n")
texts = text_splitter.split_documents(documents)

# embeddingの設定
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
db_dir = os.path.join(csv_directory, db_dir_name)
print(db_dir)
if not os.path.exists(db_dir_name):
    os.mkdir(db_dir_name)
db_dir = os.path.join(csv_directory, db_dir_name)
db = get_all_files(db_dir)

if not db:
    # ベクトルDBの作成
    db = Chroma.from_documents(texts, embedding, persist_directory = db_dir)
    # ベクトルデータをディレクトリに保存
    db.persist()

    print('Vector DB has been created.')