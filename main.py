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
import os
import openai
import subprocess

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
    # 認証情報のパスワード更新
    for index, (username, user_details) in enumerate(config['credentials']['usernames'].items()):
        user_details['password'] = passwords[index]
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
# 履歴データの作成.
#
# プロンプトと合わせて送信する履歴データを作成する
#------------------------------------------------------------------------
def create_history_data(messages):
    history_data = []
    prompt = None
    answer = None

    for message in messages:
        if message['role'] == 'user':
            prompt = message['content']
        elif message['role'] == 'assistant' and prompt is not None:
            answer = message['content'].strip()
            history_data.append({"prompt": prompt, "answer": answer})
            prompt = None
    return history_data



#------------------------------------------------------------------------
# プロンプトへの回答生成.
#
# AIプロトタイプを使ってプロンプトへの回答を生成する
#------------------------------------------------------------------------
def generete_answer(prompt, selected_prototype):

    # 設定ファイルから選択値に対応するプロトタイプ（pythonプログラム）のパスを取得する
    selected_path = [prototype[1]['path'] for prototype in sorted_prototypes if prototype[1]['title'] == selected_prototype][0]
    history_json = json.dumps(history_data)
    array_argument = [prompt, history_json]

    # プロトタイプ実行
    process  = subprocess.Popen(['python', selected_path] + array_argument, stdout=subprocess.PIPE, text=True)
    answer, _ = process .communicate()  
    return selected_prototype + "  \n" + answer



#------------------------------------------------------------------------
# プロトタイプの回答作成.
#
# プロンプトを元にAIの回答を生成する
#------------------------------------------------------------------------

# アプリの再実行の際に履歴のチャットメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力に対する反応
if prompt := st.chat_input("Please enter the prompt"):

    # 入力用の履歴データ作成
    history_data = create_history_data(st.session_state.messages)

    # 画面にプロンプトを表示
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 選択したプロトタイプ1の回答生成
    with st.spinner('回答を生成中...'):
        answer = generete_answer(prompt, selected_prototype)
        st.chat_message("assistant").markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

    # 別のプロトタイプが選択されていれば2も回答生成
    if selected_prototype == selected_prototype2:
        st.stop()
    with st.spinner('回答を生成中...'):
        answer = generete_answer(prompt, selected_prototype2)
        st.chat_message("assistant").markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
