import streamlit as st

st.markdown("""
    <style>
        h1 {
            font-size: 55px !important;
        }
        .css-62i85d.e1d0834u1 {
            background-color: #1a1a1a !important;
        }
        .css-1lr5yb2 {
            background-color: #1a1a1a !important;
        }
        .stSelectbox {
            position: sticky;
            top: 60px; /* Adjust this value to place the selectbox below the header */
            z-index: 1000;
        }
    </style>
    """, unsafe_allow_html=True)

st.title('COE-AI Chatbot')

# サイドバーにセレクトボックスを追加
options = ["prototypeA（RAGアプローチver1）", "prototypeA（RAGアプローチver2）"]
selected_option = st.sidebar.selectbox("Choose an prototype:", options)
options2 = ["prototypeA（RAGアプローチver1）", "prototypeA（RAGアプローチver2）"]
selected_option2 = st.sidebar.selectbox("Choose an prototype2:", options2)

if "messages" not in st.session_state:
    st.session_state.messages = []

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
      response1 = selected_option  + "  \n" + prompt + "→..."
      st.chat_message("assistant").markdown(response1)
      st.session_state.messages.append({"role": "assistant", "content": response1})

    if selected_option != selected_option2:
        with st.spinner('回答を生成中...'):
            response2 = selected_option2  + "  \n" + prompt + "→Why？"
            st.chat_message("assistant").markdown(response2)
            st.session_state.messages.append({"role": "assistant", "content": response2})
