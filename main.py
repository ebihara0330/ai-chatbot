import streamlit as st

st.markdown("""
    <style>
        .title {
            font = "sans-serif";
            font-size:60px !important;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)
st.title('<div class="title">COE-AI Chatbot</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# アプリの再実行の際に履歴のチャットメッセージを表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザー入力に対する反応
if prompt := st.chat_input("Databricksに関して何を知りたいですか？"):
    # チャットメッセージコンテナにユーザーメッセージを表示
    st.chat_message("user").markdown(prompt)
    # チャット履歴にユーザーメッセージを追加
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner('回答を生成中...'):
      response = "a"

    # チャットメッセージコンテナにアシスタントのレスポンスを表示
    with st.chat_message("assistant"):
      st.markdown(response)

    # チャット履歴にアシスタントのレスポンスを追加
    st.session_state.messages.append({"role": "assistant", "content": response})