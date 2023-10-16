"""
title:
coe-ai chatbotUIのメイン処理実装用

contents:
本プログラムでは以下の処理に対応する
- chatbotUIの描画
- プロンプト送信
- AIプロトタイプの実行
- AIプロトタイプの回答表示

補足）
アプリケーションではchatbotUIの表示内容とプロトタイプの実行処理をサーバロジックに記述するのみ
クライアントで必要なchatbotUIの描画、プロンプト送信、AIの回答描画はstreamlit側で対応する
"""
import streamlit as st
import os
import json
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

#------------------------------------------------------------------------
# Basic認証.
#
# 入力値を所定のパスワードと照合する
#------------------------------------------------------------------------

# 画面タイトルの設定
st.title('COE-AI Chatbot')

# Basic認証
def check_password():
    # ユーザ情報取得
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    # パスワード取得・ハッシュ化
    passwords = json.loads(os.environ.get('password') if 'password' in os.environ else st.secrets["password"])
    hashed_passwords = stauth.Hasher(passwords).generate()
    # 認証情報のパスワード更新
    for index, (username, user_details) in enumerate(config['credentials']['usernames'].items()):
        user_details['password'] = hashed_passwords[index]
    # authenticatorに認証情報設定
    authenticator = stauth.Authenticate(
        config['credentials'], config['cookie']['name'], config['cookie']['key'],config['cookie']['expiry_days']
    )
    # ログイン画面表示＆認証
    authenticator.login('Login', 'main')
    if st.session_state["authentication_status"]:
        return True
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    return False

# Basic認証の呼び出し（OKなら後続処理実行）
if not check_password():
    st.stop()



#------------------------------------------------------------------------
# 初期化.
#
# メッセージの表示内容とプロトタイプの選択値などを定義
#------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "prev_selection" not in st.session_state:
    st.session_state.prev_selection = None



#------------------------------------------------------------------------
# chatbotUIのデザイン・レイアウト定義.
#
# stremlitのコンポーネントを使ってUIを構成する
#------------------------------------------------------------------------

# フォントサイズ・画像背景の設定
st.markdown("""
    <style>
        h1 {
            font-size: 55px !important;
        }
        .css-62i85d, .css-1lr5yb2 {
            background-color: #1a1a1a !important;
        }
        .css-1yrzt5d, .css-usjmio {
            background-color: #f5f5f5 !important;
        }
    </style>
    """, unsafe_allow_html=True)
# 設定ファイル（config.json）からプロトタイプ読み込み
with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
# プロトタイプを更新日降順でソート
sorted_prototypes = sorted(config['prototype'].items(), key=lambda x: x[1]['updatedate'], reverse=True)
titles = [prototype[1]['title'] for prototype in sorted_prototypes]
# プロトタイプ選択用のセレクトボックス（比較用に2つ）をサイドバーに設置
selected_prototype = st.sidebar.selectbox('Select a Prototype:', titles)
selected_prototype2 = st.sidebar.selectbox('Select a Prototype2:', titles)



#------------------------------------------------------------------------
# プロトタイプの更新制御.
#
# 状態が変化したら画面の表示内容を初期化する
#------------------------------------------------------------------------
if st.session_state.prev_selection != selected_prototype + selected_prototype2 :
    st.session_state.messages = []
    st.session_state.prev_selection = selected_prototype + selected_prototype2



#------------------------------------------------------------------------
# プロトタイプの回答作成.
#
# プロンプトを元にAIの回答を生成する
#------------------------------------------------------------------------

#--------------------------------------------------------------

import requests
import json

# 与えられた情報を設定
OPENAI_API_TYPE = 'azure'
OPENAI_API_HOST = 'https://testopennetwork.openai.azure.com/'
OPENAI_API_KEY = 'fc9f375146314c79b2e30139e15240a2'
AZURE_DEPLOYMENT_ID = 'gpt-35-turbo2'

# エンドポイントURLを構築
endpoint_url = f"{OPENAI_API_HOST}v1/engines/{AZURE_DEPLOYMENT_ID}/completions"

# ヘッダーを設定
headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

# リクエストデータを設定
data = {
    "prompt": "Translate the following English text to French: 'Hello, how are you?'",
    "max_tokens": 60
}

# POSTリクエストを送信
response = requests.post(endpoint_url, headers=headers, json=data)

# 応答をチェック
if response.status_code == 200:
    # 成功: 応答をJSONとして解析し、結果を表示
    response_json = response.json()
    print(response_json['choices'][0]['text'])
    st.write(response_json['choices'][0]['text'])
else:
    # エラー: エラーメッセージを表示
    print(f"Error: {response.status_code}")
    print(response.text)
    st.write(response.text)
#--------------------------------------------------------------

# アプリの再実行の際に履歴のチャットメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力に対する反応
if prompt := st.chat_input("Please enter the prompt"):

    # チャットメッセージコンテナにユーザーメッセージを表示
    st.chat_message("user").markdown(prompt)
    # チャット履歴にユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner('回答を生成中...'):
      response1 = selected_prototype  + "  \n" + prompt + "→xxxx1"
      st.chat_message("assistant").markdown(response1)
      st.session_state.messages.append({"role": "assistant", "content": response1})

    if selected_prototype != selected_prototype2:
        with st.spinner('回答を生成中...'):
            response2 = selected_prototype2  + "  \n" + prompt + "→xxxx2"
            st.chat_message("assistant").markdown(response2)
            st.session_state.messages.append({"role": "assistant", "content": response2})
